"""Instrumentación temporal y optativa para scroll y navegación.

Activación: CALCULADORA_DIAGNOSTICO_UI=1 antes de iniciar la aplicación.
El registro se escribe en %TEMP%/CalculadoraAlgebra-diagnostico.log.
"""

import json
import os
import tempfile
import time
import uuid
from collections import defaultdict
from functools import wraps


ACTIVO = os.environ.get("CALCULADORA_DIAGNOSTICO_UI", "").strip() == "1"
RUTA_LOG = os.path.join(tempfile.gettempdir(), "CalculadoraAlgebra-diagnostico.log")
SESION = uuid.uuid4().hex[:12]


def registrar(tipo, **datos):
    if not ACTIVO:
        return
    registro = {"ts": time.time(), "sesion": SESION, "tipo": tipo, **datos}
    try:
        with open(RUTA_LOG, "a", encoding="utf-8") as archivo:
            archivo.write(json.dumps(registro, ensure_ascii=False, default=str) + "\n")
    except OSError:
        # La instrumentación nunca debe impedir que la interfaz siga funcionando.
        pass


def contar_widgets(widget):
    """Cuenta recursivamente widgets Tk vivos, tolerando ventanas destruidas."""
    try:
        hijos = widget.winfo_children()
    except Exception:
        return 0
    return 1 + sum(contar_widgets(hijo) for hijo in hijos)


class MedidorScroll:
    """Acumula eventos de geometría y emite un resumen al quedar inactivo."""

    def __init__(self, contenedor):
        self.contenedor = contenedor
        self.eventos = 0
        self.actualizaciones = 0
        self.duraciones = []
        self.configures = 0
        self.burst = 0
        self.burst_max = 0
        self.ultimo_configure = None
        self.ultimo_ancho_ventana = None
        self.anchos_ventana_cambiados = 0
        self.anomalias = []
        self.after_id = None
        self.ultimo_estado = None
        self.creado = time.perf_counter()
        self.clasificaciones = defaultdict(int)
        self.interacciones = defaultdict(int)
        self.arrastrando = False
        self.arrastre_inicio = None
        self.arrastre_inicial = None
        self.arrastre_primera_muestra = None
        self.arrastre_ultimo = None
        self.arrastre_muestras = 0
        self.arrastre_configures = 0
        self.arrastre_actualizaciones = 0
        self.arrastre_cambios_geometria = []
        self.arrastre_yview_min = None
        self.arrastre_yview_max = None
        self.arrastre_thumb_min = None
        self.arrastre_thumb_max = None
        self.arrastre_press = None
        self.arrastre_primera_posicion = None
        self.arrastre_ultima_posicion = None

    def configure(self, origen):
        ahora = time.perf_counter()
        self.eventos += 1
        if self.ultimo_configure is None or ahora - self.ultimo_configure > 0.12:
            self.burst = 1
        else:
            self.burst += 1
        self.burst_max = max(self.burst_max, self.burst)
        self.ultimo_configure = ahora
        self.configures += 1
        if self.arrastrando:
            self.arrastre_configures += 1
        self.ultimo_origen = origen
        estado = self._estado()
        if self.arrastrando:
            self._capturar_geometria_arrastre(estado, "configure_antes_actualizar")
        anterior = self.ultimo_estado
        if self.arrastrando:
            clase = "durante_arrastre"
        elif ahora - self.creado < 1.5 and self.actualizaciones < 8:
            clase = "construccion_inicial"
        elif anterior and estado.get("canvas_px") != anterior.get("canvas_px"):
            clase = "redimensionamiento"
        elif anterior and estado.get("yview") != anterior.get("yview"):
            clase = "desplazamiento"
        else:
            clase = "geometria"
        self.clasificaciones[clase] += 1
        self.actualizar("configure:" + origen)

    def _estado(self):
        c = self.contenedor
        canvas = c._lienzo
        try:
            bbox = canvas.bbox("all")
            region = canvas.cget("scrollregion")
            ancho_ventana = canvas.itemcget(c._ventana, "width")
            ancho_ventana = float(ancho_ventana) if ancho_ventana else None
            return {
                "canvas_px": [canvas.winfo_width(), canvas.winfo_height()],
                "interior_req": [c.interior.winfo_reqwidth(), c.interior.winfo_reqheight()],
                "interior_real": [c.interior.winfo_width(), c.interior.winfo_height()],
                "scrollregion": region,
                "bbox_all": bbox,
                "ventana_ancho": ancho_ventana,
                "scrollbar_thumb": list(c._barra_v.get()),
                "yview": canvas.yview(),
                "xview": canvas.xview(),
            }
        except Exception as error:
            return {"error_estado": str(error)}

    def actualizar(self, origen):
        antes = self._estado()
        inicio = time.perf_counter()
        try:
            self.contenedor._diagnostico_actualizar_original()
        finally:
            ms = (time.perf_counter() - inicio) * 1000
            despues = self._estado()
            self.actualizaciones += 1
            if self.arrastrando:
                self.arrastre_actualizaciones += 1
                self._capturar_geometria_arrastre(despues, "configure_despues_actualizar")
            self.duraciones.append(ms)
            self.ultimo_estado = despues
            if antes.get("ventana_ancho") != despues.get("ventana_ancho"):
                self.anchos_ventana_cambiados += 1
            if antes.get("canvas_px") != despues.get("canvas_px"):
                self.anomalias.append({"tipo": "canvas_cambio", "antes": antes, "despues": despues})
            if antes.get("interior_real") != despues.get("interior_real"):
                self.anomalias.append({"tipo": "interior_cambio", "antes": antes, "despues": despues})
            if despues.get("bbox_all") and despues.get("scrollregion"):
                try:
                    region = [float(v) for v in str(despues["scrollregion"]).split()]
                    bbox = list(despues["bbox_all"])
                    if len(region) == 4 and any(abs(a - b) > 1 for a, b in zip(region, bbox)):
                        self.anomalias.append({"tipo": "scrollregion_difiere_bbox", "region": region, "bbox": bbox})
                except (TypeError, ValueError):
                    pass
        if self.after_id is not None:
            try:
                self.contenedor.after_cancel(self.after_id)
            except Exception:
                pass
        try:
            self.after_id = self.contenedor.after(900, self.flush)
        except Exception:
            self.flush()

    def flush(self):
        if not self.eventos and not self.actualizaciones and not self.interacciones:
            return
        duraciones = self.duraciones
        c = self.contenedor
        if self.arrastrando:
            registrar(
                "scroll_arrastre_checkpoint",
                contenedor=str(c),
                estado="en_curso_sin_release",
                press=self.arrastre_press,
                movimientos_muestreados=self.arrastre_muestras,
                configures_durante_arrastre=self.arrastre_configures,
                actualizaciones_durante_arrastre=self.arrastre_actualizaciones,
                estado_geometrico=self.arrastre_ultimo,
            )
        modulo = None
        try:
            raiz = c.winfo_toplevel()
            paneles = getattr(raiz, "paneles", {})
            actual = c
            while actual is not None:
                for nombre, panel in paneles.items():
                    if actual is panel:
                        modulo = nombre
                        break
                if modulo is not None:
                    break
                actual = getattr(actual, "master", None)
        except Exception:
            pass
        registrar(
            "scroll_resumen",
            contenedor=str(c),
            clase=type(c).__name__,
            modulo=modulo or getattr(c, "_diagnostico_modulo", None),
            eventos_configure=self.configures,
            actualizaciones=self.actualizaciones,
            origen=getattr(self, "ultimo_origen", "inicial"),
            clasificacion_configure=dict(self.clasificaciones),
            burst_max_120ms=self.burst_max,
            ancho_ventana_cambios=self.anchos_ventana_cambiados,
            actualizar_ms={
                "min": min(duraciones) if duraciones else 0,
                "max": max(duraciones) if duraciones else 0,
                "promedio": sum(duraciones) / len(duraciones) if duraciones else 0,
            },
            estado=self.ultimo_estado,
            anomalias=self.anomalias[-20:],
            anomalias_total=len(self.anomalias),
            interacciones=dict(self.interacciones),
            arrastre_activo=self.arrastrando,
        )
        self.eventos = self.actualizaciones = self.configures = 0
        self.duraciones.clear()
        self.clasificaciones.clear()
        self.interacciones.clear()
        self.anchos_ventana_cambiados = self.burst_max = 0
        self.anomalias.clear()
        self.after_id = None

    def interaccion(self, tipo):
        self.interacciones[tipo] += 1
        self.ultimo_estado = self._estado()
        if self.after_id is not None:
            try:
                self.contenedor.after_cancel(self.after_id)
            except Exception:
                pass
        try:
            self.after_id = self.contenedor.after(900, self.flush)
        except Exception:
            self.flush()

    def iniciar_arrastre(self, press_info=None):
        if self.arrastrando:
            self.terminar_arrastre("nuevo_press_antes_de_release")
        self.arrastrando = True
        self.arrastre_inicio = time.perf_counter()
        self.arrastre_inicial = self._estado()
        self.arrastre_press = press_info or {}
        self.arrastre_ultimo = self.arrastre_inicial
        self.arrastre_primera_muestra = None
        self.arrastre_primera_posicion = None
        self.arrastre_ultima_posicion = None
        self.arrastre_muestras = 0
        self.arrastre_configures = 0
        self.arrastre_actualizaciones = 0
        self.arrastre_cambios_geometria = []
        y = self.arrastre_inicial.get("yview")
        thumb = self.arrastre_inicial.get("scrollbar_thumb")
        self.arrastre_yview_min = self.arrastre_yview_max = list(y) if y else None
        self.arrastre_thumb_min = self.arrastre_thumb_max = list(thumb) if thumb else None
        self.interaccion("arrastre_vertical_inicio")

    @staticmethod
    def _posicion_evento(evento):
        if evento is None:
            return None
        return {"x": getattr(evento, "x", None), "y": getattr(evento, "y", None)}

    @staticmethod
    def _info_widget(widget):
        info = {"widget": str(widget) if widget is not None else None}
        try:
            info["clase_widget"] = widget.winfo_class()
        except Exception:
            info["clase_widget"] = type(widget).__name__ if widget is not None else None
        return info

    def mover_arrastre(self, evento=None):
        # B1-Motion es el evento que CTkScrollbar usa para mover el thumb.
        if not self.arrastrando:
            return
        estado = self._estado()
        self.arrastre_muestras += 1
        if self.arrastre_primera_muestra is None:
            self.arrastre_primera_muestra = estado
            self.arrastre_primera_posicion = self._posicion_evento(evento)
        self.arrastre_ultima_posicion = self._posicion_evento(evento)
        y = estado.get("yview")
        thumb = estado.get("scrollbar_thumb")
        if y:
            if self.arrastre_yview_min is None:
                self.arrastre_yview_min = list(y)
                self.arrastre_yview_max = list(y)
            else:
                self.arrastre_yview_min = [min(a, b) for a, b in zip(self.arrastre_yview_min, y)]
                self.arrastre_yview_max = [max(a, b) for a, b in zip(self.arrastre_yview_max, y)]
        if thumb:
            if self.arrastre_thumb_min is None:
                self.arrastre_thumb_min = list(thumb)
                self.arrastre_thumb_max = list(thumb)
            else:
                self.arrastre_thumb_min = [min(a, b) for a, b in zip(self.arrastre_thumb_min, thumb)]
                self.arrastre_thumb_max = [max(a, b) for a, b in zip(self.arrastre_thumb_max, thumb)]
        self._capturar_geometria_arrastre(estado, "movimiento")
        self.interacciones["arrastre_vertical_movimiento"] += 1

    def _capturar_geometria_arrastre(self, estado, origen):
        anterior = self.arrastre_ultimo or estado
        dimensiones = ("canvas_px", "interior_req", "interior_real", "ventana_ancho")
        cambiaron = [k for k in dimensiones if anterior.get(k) != estado.get(k)]
        if cambiaron and len(self.arrastre_cambios_geometria) < 30:
            self.arrastre_cambios_geometria.append({
                "muestra": self.arrastre_muestras,
                "origen": origen,
                "campos": cambiaron,
                "antes": {k: anterior.get(k) for k in cambiaron},
                "despues": {k: estado.get(k) for k in cambiaron},
                "scrollregion": estado.get("scrollregion"),
                "bbox_all": estado.get("bbox_all"),
            })
        self.arrastre_ultimo = estado

    def registrar_press(self, evento, item_id, tags, reconocido, motivo):
        info = {
            **self._info_widget(getattr(evento, "widget", None)),
            "coordenadas": self._posicion_evento(evento),
            "elemento_actual": item_id,
            "tags": list(tags),
            "thumb": self._estado().get("scrollbar_thumb"),
            "yview": self._estado().get("yview"),
            "reconocido_como_thumb": bool(reconocido),
            "clasificacion": ("reconocido" if reconocido else
                              "indeterminado" if item_id is None else "rechazado"),
            "motivo_rechazo": motivo if not reconocido and item_id is not None else None,
            "motivo_indeterminado": motivo if item_id is None else None,
        }
        registrar("scroll_press", **info)
        return info

    def registrar_release_sin_sesion(self, evento):
        registrar("scroll_release", **self._info_widget(getattr(evento, "widget", None)),
                  coordenadas=self._posicion_evento(evento), sesion_activa=False)

    def info_release(self, evento):
        estado = self._estado()
        return {
            **self._info_widget(getattr(evento, "widget", None)),
            "coordenadas": self._posicion_evento(evento),
            "thumb": estado.get("scrollbar_thumb"),
            "yview": estado.get("yview"),
            "sesion_activa": True,
        }

    def terminar_arrastre(self, motivo="soltar", release_info=None):
        if self.arrastrando:
            final = self._estado()
            duracion = time.perf_counter() - self.arrastre_inicio
            release_recibido = release_info is not None
            reconocido = bool(self.arrastre_press.get("reconocido_como_thumb"))
            if release_recibido:
                registrar("scroll_release", **release_info)
            registrar(
                "scroll_arrastre",
                contenedor=str(self.contenedor),
                estado=("completa" if reconocido and release_recibido else
                        "incompleta" if not release_recibido else
                        "press_rechazado" if self.arrastre_press.get("clasificacion") == "rechazado" else
                        "indeterminada"),
                motivo=motivo,
                press_recibido=True,
                press_reconocido=reconocido,
                press_clasificacion=self.arrastre_press.get("clasificacion"),
                press_rechazado=self.arrastre_press.get("clasificacion") == "rechazado",
                press=self.arrastre_press,
                movimiento_recibido=self.arrastre_muestras > 0,
                release_recibido=release_recibido,
                sesion_completa=reconocido and release_recibido,
                sesion_incompleta=not release_recibido,
                release=release_info,
                duracion_ms=duracion * 1000,
                movimientos_muestreados=self.arrastre_muestras,
                primera_posicion=self.arrastre_primera_posicion,
                ultima_posicion=self.arrastre_ultima_posicion,
                configures_durante_arrastre=self.arrastre_configures,
                actualizaciones_durante_arrastre=self.arrastre_actualizaciones,
                inicio=self.arrastre_inicial,
                primera_muestra=self.arrastre_primera_muestra,
                fin=final,
                rango_yview=[self.arrastre_yview_min, self.arrastre_yview_max],
                rango_thumb=[self.arrastre_thumb_min, self.arrastre_thumb_max],
                cambios_geometricos=self.arrastre_cambios_geometria,
            )
            self.interacciones["arrastre_vertical_fin"] += 1
            self.arrastrando = False
            self.arrastre_inicio = None
            self.flush()


def instrumentar_scroll(contenedor):
    if not ACTIVO:
        return None
    medidor = MedidorScroll(contenedor)
    contenedor._diagnostico_scroll = medidor
    # Mantiene la operación original y mide sin cambiar su geometría ni resultado.
    contenedor._diagnostico_actualizar_original = contenedor._actualizar
    contenedor._actualizar = lambda: medidor.actualizar("invocacion_directa")
    return medidor


class MedidorScrollInicio:
    """Observa, sin sustituir callbacks, el scroll del CTkScrollableFrame de Inicio."""

    def __init__(self, inicio, canvas_contenido, scrollbar, canvas_barra):
        self.inicio = inicio
        self.canvas = canvas_contenido
        self.scrollbar = scrollbar
        self.canvas_barra = canvas_barra
        self.activa = False
        self.inicio_monotonic = None
        self.press = None
        self.movimientos = 0
        self.configures = defaultdict(int)
        self.yview_min = None
        self.yview_max = None
        self.ultimo_estado = None
        self.cambios_geometricos = []
        self.primera_posicion = None
        self.ultima_posicion = None
        self.after_id = None
        self.eventos_configure = defaultdict(lambda: defaultdict(int))
        self.metricas_callbacks = defaultdict(int)
        self.metricas_inicio_sesion = {}
        self.session_cambios = defaultdict(int)
        self.session_configures = defaultdict(int)
        self.configure_anterior = {}
        self.muestras_movimiento = []
        self.ultimo_scrollregion_solicitado = None
        self._envolver_callbacks_geometria()

        # CTkScrollbar.bind() también reenvía al Canvas interno con add=True;
        # usarlo directamente deja explícito qué widget recibe los eventos.
        canvas_barra.bind("<ButtonPress-1>", self.press_evento, add="+")
        canvas_barra.bind("<B1-Motion>", self.movimiento_evento, add="+")
        canvas_barra.bind("<ButtonRelease-1>", self.release_evento, add="+")
        canvas_barra.bind("<Configure>", lambda evento: self.configure_evento(evento, "canvas_scrollbar"), add="+")
        canvas_contenido.bind("<Configure>", lambda evento: self.configure_evento(evento, "canvas_contenido"), add="+")
        inicio.bind("<Configure>", lambda evento: self.configure_evento(evento, "frame_contenido"), add="+")

    def _envolver_callbacks_geometria(self):
        """Cuenta llamadas relevantes y delega cada llamada sin alterar argumentos."""
        canvas = self.canvas
        configure_original = canvas.configure

        def configure_observado(*args, **kwargs):
            opciones = dict(args[0]) if args and isinstance(args[0], dict) else {}
            opciones.update(kwargs)
            if "scrollregion" in opciones:
                valor = opciones["scrollregion"]
                self.metricas_callbacks["scrollregion_llamadas"] += 1
                if valor == self.ultimo_scrollregion_solicitado:
                    self.metricas_callbacks["scrollregion_repetido"] += 1
                else:
                    self.metricas_callbacks["scrollregion_cambios_solicitados"] += 1
                    self.ultimo_scrollregion_solicitado = valor
                if self.activa and len(self.cambios_geometricos) < 30:
                    self.cambios_geometricos.append({
                        "origen": "canvas.configure(scrollregion)",
                        "valor": valor,
                    })
            if "width" in opciones or "height" in opciones:
                self.metricas_callbacks["canvas_configure_dimensiones"] += 1
            self.metricas_callbacks["canvas_configure_total"] += 1
            inicio_tiempo = time.perf_counter()
            try:
                return configure_original(*args, **kwargs)
            finally:
                self.metricas_callbacks["canvas_configure_ms_total"] += (
                    time.perf_counter() - inicio_tiempo
                ) * 1000

        canvas.configure = configure_observado
        itemconfigure_original = canvas.itemconfigure

        def itemconfigure_observado(tag_or_id, *args, **kwargs):
            opciones = dict(args[0]) if args and isinstance(args[0], dict) else {}
            opciones.update(kwargs)
            es_ventana = tag_or_id == getattr(self.inicio, "_create_window_id", None)
            if es_ventana:
                self.metricas_callbacks["ventana_itemconfigure_total"] += 1
                if "width" in opciones or "height" in opciones:
                    self.metricas_callbacks["ventana_itemconfigure_dimensiones"] += 1
                    if self.activa and len(self.cambios_geometricos) < 30:
                        self.cambios_geometricos.append({
                            "origen": "canvas.itemconfigure(ventana)",
                            "opciones": {k: opciones[k] for k in ("width", "height") if k in opciones},
                        })
            inicio_tiempo = time.perf_counter()
            try:
                return itemconfigure_original(tag_or_id, *args, **kwargs)
            finally:
                self.metricas_callbacks["ventana_itemconfigure_ms_total"] += (
                    time.perf_counter() - inicio_tiempo
                ) * 1000

        canvas.itemconfigure = itemconfigure_observado

        frame_configure_original = self.inicio.configure

        def frame_configure_observado(*args, **kwargs):
            opciones = dict(args[0]) if args and isinstance(args[0], dict) else {}
            opciones.update(kwargs)
            self.metricas_callbacks["frame_configure_total"] += 1
            if "width" in opciones or "height" in opciones:
                self.metricas_callbacks["frame_configure_dimensiones"] += 1
                if self.activa and len(self.cambios_geometricos) < 30:
                    self.cambios_geometricos.append({
                        "origen": "frame.configure(dimensiones)",
                        "opciones": {k: opciones[k] for k in ("width", "height") if k in opciones},
                    })
            inicio_tiempo = time.perf_counter()
            try:
                return frame_configure_original(*args, **kwargs)
            finally:
                self.metricas_callbacks["frame_configure_ms_total"] += (
                    time.perf_counter() - inicio_tiempo
                ) * 1000

        self.inicio.configure = frame_configure_observado

        dibujar = getattr(self.scrollbar, "_draw", None)
        if dibujar is not None:
            def dibujar_observado(*args, **kwargs):
                inicio = time.perf_counter()
                self.metricas_callbacks["scrollbar_draw_total"] += 1
                try:
                    return dibujar(*args, **kwargs)
                finally:
                    self.metricas_callbacks["scrollbar_draw_ms_total"] += (
                        time.perf_counter() - inicio
                    ) * 1000

            self.scrollbar._draw = dibujar_observado
            actualizar = getattr(self.canvas_barra, "update_idletasks", None)
            if actualizar is not None:
                def actualizar_observado(*args, **kwargs):
                    self.metricas_callbacks["update_idletasks_total"] += 1
                    return actualizar(*args, **kwargs)

                self.canvas_barra.update_idletasks = actualizar_observado

    def _estado(self):
        try:
            bbox = self.canvas.bbox("all")
        except Exception:
            bbox = None
        try:
            region = self.canvas.cget("scrollregion")
        except Exception:
            region = None
        try:
            yview = tuple(self.canvas.yview())
        except Exception:
            yview = None
        try:
            thumb = tuple(self.scrollbar.get())
        except Exception:
            # Si la barra no permite consultar el thumb, usar el rango actual
            # que el Canvas comunica mediante yscrollcommand.
            thumb = yview
        try:
            canvas_dimensiones = [self.canvas.winfo_width(), self.canvas.winfo_height()]
            canvas_solicitadas = [self.canvas.winfo_reqwidth(), self.canvas.winfo_reqheight()]
        except Exception:
            canvas_dimensiones = None
            canvas_solicitadas = None
        try:
            frame_dimensiones = [self.inicio.winfo_width(), self.inicio.winfo_height()]
            frame_solicitadas = [self.inicio.winfo_reqwidth(), self.inicio.winfo_reqheight()]
        except Exception:
            frame_dimensiones = None
            frame_solicitadas = None
        try:
            ventana_dimensiones = [
                self.canvas.itemcget(self.inicio._create_window_id, "width"),
                self.canvas.itemcget(self.inicio._create_window_id, "height"),
            ]
            ventana_coordenadas = self.canvas.coords(self.inicio._create_window_id)
        except Exception:
            ventana_dimensiones, ventana_coordenadas = None, None
        return {
            "canvas_contenido": canvas_dimensiones,
            "canvas_solicitadas": canvas_solicitadas,
            "frame_contenido": frame_dimensiones,
            "frame_solicitadas": frame_solicitadas,
            "ventana_embebida": ventana_dimensiones,
            "ventana_coordenadas": ventana_coordenadas,
            "scrollregion": region,
            "bbox_all": bbox,
            "yview": yview,
            "thumb": thumb,
        }

    @staticmethod
    def _posicion(evento):
        return {"x": getattr(evento, "x", None), "y": getattr(evento, "y", None)}

    def _elemento_actual(self, evento):
        item_id, tags = None, ()
        identificador = None
        if hasattr(self.canvas_barra, "find_withtag"):
            try:
                items = self.canvas_barra.find_withtag("current")
                item_id = items[-1] if items else None
                if item_id is not None:
                    tags = tuple(self.canvas_barra.gettags(item_id))
            except Exception:
                pass
        else:
            try:
                identificador = self.canvas_barra.identify(
                    getattr(evento, "x", 0), getattr(evento, "y", 0)
                )
            except Exception:
                identificador = None
        if "scrollbar_parts" in tags or identificador == "slider":
            tipo = "thumb"
        elif "border_parts" in tags or (identificador or "").startswith("trough"):
            tipo = "pista"
        elif item_id is None and not identificador:
            tipo = "indeterminado"
        else:
            tipo = "otro_elemento"
        return {
            "widget": str(getattr(evento, "widget", None)),
            "clase_widget": type(getattr(evento, "widget", None)).__name__,
            "coordenadas": self._posicion(evento),
            "elemento_canvas": item_id,
            "elemento_ttk": identificador,
            "tags": list(tags),
            "elemento": tipo,
        }

    def _capturar_cambios(self, estado, origen):
        anterior = self.ultimo_estado or estado
        claves = (
            "canvas_contenido", "canvas_solicitadas", "frame_contenido",
            "frame_solicitadas", "ventana_embebida", "ventana_coordenadas",
            "scrollregion", "bbox_all", "yview",
        )
        cambiaron = [clave for clave in claves if anterior.get(clave) != estado.get(clave)]
        if self.activa:
            for clave in cambiaron:
                self.session_cambios[clave] += 1
            if not cambiaron:
                self.session_cambios["muestra_sin_cambio"] += 1
        if cambiaron and len(self.cambios_geometricos) < 30:
            self.cambios_geometricos.append({
                "movimiento": self.movimientos,
                "origen": origen,
                "campos": cambiaron,
                "antes": {clave: anterior.get(clave) for clave in cambiaron},
                "despues": {clave: estado.get(clave) for clave in cambiaron},
            })
        self.ultimo_estado = estado

    def press_evento(self, evento):
        if self.activa:
            self._finalizar("nuevo_press_sin_release", release=None)
        self.activa = True
        self.inicio_monotonic = time.perf_counter()
        self.press = self._elemento_actual(evento)
        self.movimientos = 0
        self.configures.clear()
        self.session_cambios = defaultdict(int)
        self.session_configures = defaultdict(int)
        self.metricas_inicio_sesion = dict(self.metricas_callbacks)
        self.configure_anterior.clear()
        self.muestras_movimiento = []
        self.cambios_geometricos = []
        self.primera_posicion = self.ultima_posicion = None
        estado = self._estado()
        self.yview_min = self.yview_max = list(estado["yview"]) if estado["yview"] else None
        self.ultimo_estado = estado
        press_log = self.press
        self.press = {**press_log, "estado": estado}
        self._capturar_cambios(estado, "press")
        registrar(
            "dashboard_scroll_press",
            pantalla="Inicio / Dashboard / CTkScrollableFrame",
            variante=getattr(self.inicio, "_diagnostico_scrollbar_variante", "ctk"),
            **press_log,
            estado=estado,
        )
        self._programar_checkpoint()

    def movimiento_evento(self, evento):
        if not self.activa:
            return
        posicion = self._posicion(evento)
        if self.primera_posicion is None:
            self.primera_posicion = posicion
        self.ultima_posicion = posicion
        self.movimientos += 1
        estado = self._estado()
        yview = estado.get("yview")
        if yview:
            if self.yview_min is None:
                self.yview_min = self.yview_max = list(yview)
            else:
                self.yview_min = [min(a, b) for a, b in zip(self.yview_min, yview)]
                self.yview_max = [max(a, b) for a, b in zip(self.yview_max, yview)]
        estado_anterior = self.ultimo_estado
        self._capturar_cambios(estado, "movimiento")
        if (self.movimientos == 1 or self.movimientos % 25 == 0
                or estado_anterior is None or estado_anterior.get("yview") != estado.get("yview")):
            if len(self.muestras_movimiento) < 40:
                self.muestras_movimiento.append({
                    "n": self.movimientos,
                    "posicion": posicion,
                    "yview": estado.get("yview"),
                    "canvas": estado.get("canvas_contenido"),
                    "frame": estado.get("frame_contenido"),
                    "scrollregion": estado.get("scrollregion"),
                    "bbox_all": estado.get("bbox_all"),
                })
        self._programar_checkpoint()

    def configure_evento(self, evento, origen):
        self.configures[origen] += 1
        metricas = self.eventos_configure[origen]
        metricas["total"] += 1
        estado = self._estado()
        anterior = self.configure_anterior.get(origen)
        campos_geometria = (
            "canvas_contenido", "canvas_solicitadas", "frame_contenido",
            "frame_solicitadas", "ventana_embebida", "ventana_coordenadas",
        )
        campos_scroll = ("scrollregion", "bbox_all", "yview")
        cambios = [
            clave for clave in (*campos_geometria, *campos_scroll)
            if anterior is not None and anterior.get(clave) != estado.get(clave)
        ]
        if anterior is None or not cambios:
            metricas["sin_cambio"] += 1
        if any(clave in campos_geometria for clave in cambios):
            metricas["geometria_cambio"] += 1
        if "scrollregion" in cambios:
            metricas["scrollregion_cambio"] += 1
        if "bbox_all" in cambios:
            metricas["bbox_cambio"] += 1
        if "yview" in cambios:
            metricas["yview_cambio"] += 1
        self.configure_anterior[origen] = estado
        if self.activa:
            self.session_configures[origen] += 1
            if anterior is not None and not cambios:
                self.session_cambios["configure_sin_cambio"] += 1
            self._capturar_cambios(estado, "configure:" + origen)

    def release_evento(self, evento):
        if not self.activa:
            registrar(
                "dashboard_scroll_release",
                pantalla="Inicio / Dashboard / CTkScrollableFrame",
                variante=getattr(self.inicio, "_diagnostico_scrollbar_variante", "ctk"),
                widget=str(getattr(evento, "widget", None)),
                coordenadas=self._posicion(evento),
                sesion_activa=False,
            )
            return
        release = {
            "widget": str(getattr(evento, "widget", None)),
            "coordenadas": self._posicion(evento),
        }
        self._finalizar("release", release)

    def _programar_checkpoint(self):
        if self.after_id is not None:
            try:
                self.inicio.after_cancel(self.after_id)
            except Exception:
                pass
        try:
            self.after_id = self.inicio.after(1800, self._checkpoint)
        except Exception:
            self.after_id = None

    def _checkpoint(self):
        self.after_id = None
        if self.activa:
            registrar(
                "dashboard_scroll_checkpoint",
                pantalla="Inicio / Dashboard / CTkScrollableFrame",
                variante=getattr(self.inicio, "_diagnostico_scrollbar_variante", "ctk"),
                estado="sin_release_aun",
                movimientos_recibidos=self.movimientos,
                configures=dict(self.configures),
                callbacks=self._metricas_sesion(),
                cambios=dict(self.session_cambios),
                geometria=self._estado(),
            )

    def _finalizar(self, motivo, release):
        final = self._estado()
        self._capturar_cambios(final, "release" if release else "finalizacion_sin_release")
        inicio_yview = (self.press or {}).get("estado", {}).get("yview")
        yview_final = final.get("yview")
        duration_ms = ((time.perf_counter() - self.inicio_monotonic) * 1000
                       if self.inicio_monotonic is not None else 0)
        if self.after_id is not None:
            try:
                self.inicio.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None
        registrar(
            "dashboard_scroll_release",
            pantalla="Inicio / Dashboard / CTkScrollableFrame",
            variante=getattr(self.inicio, "_diagnostico_scrollbar_variante", "ctk"),
            release_recibido=release is not None,
            release=release,
            sesion_activa=True,
        )
        registrar(
            "dashboard_scroll_arrastre",
            pantalla="Inicio / Dashboard / CTkScrollableFrame",
            variante=getattr(self.inicio, "_diagnostico_scrollbar_variante", "ctk"),
            estado="completa" if release is not None else "incompleta",
            motivo=motivo,
            press=self.press,
            press_reconocido=(self.press or {}).get("elemento") == "thumb",
            movimientos_recibidos=self.movimientos,
            primera_posicion=self.primera_posicion,
            ultima_posicion=self.ultima_posicion,
            yview_inicio=inicio_yview,
            yview_fin=yview_final,
            rango_yview=[self.yview_min, self.yview_max],
            duracion_ms=duration_ms,
            configures=dict(self.configures),
            configures_total=sum(self.configures.values()),
            configures_acumulados={origen: dict(datos) for origen, datos in self.eventos_configure.items()},
            configures_durante_arrastre=dict(self.session_configures),
            cambios_por_configure=dict(self.session_cambios),
            callbacks_durante_arrastre=self._metricas_sesion(),
            movimientos_muestreados=self.muestras_movimiento,
            cambios_geometricos=self.cambios_geometricos,
            geometria_inicio=(self.press or {}).get("estado"),
            geometria_fin=final,
        )
        self.activa = False
        self.inicio_monotonic = None
        self.press = None

    def _metricas_sesion(self):
        return {
            nombre: valor - self.metricas_inicio_sesion.get(nombre, 0)
            for nombre, valor in self.metricas_callbacks.items()
        }


def instrumentar_inicio(inicio):
    """Instala observadores aditivos solo sobre el scroll vertical del Dashboard."""
    if not ACTIVO or getattr(inicio, "_diagnostico_scroll_inicio", None) is not None:
        return getattr(inicio, "_diagnostico_scroll_inicio", None)
    canvas_contenido = getattr(inicio, "_parent_canvas", None)
    scrollbar = (getattr(inicio, "_diagnostico_scrollbar_activo", None)
                 or getattr(inicio, "_scrollbar", None))
    canvas_barra = getattr(scrollbar, "_canvas", scrollbar)
    if canvas_contenido is None or scrollbar is None or canvas_barra is None:
        registrar(
            "dashboard_scroll_instrumentacion_error",
            pantalla="Inicio / Dashboard / CTkScrollableFrame",
            frame=type(inicio).__name__,
            canvas_disponible=canvas_contenido is not None,
            scrollbar_disponible=scrollbar is not None,
            canvas_scrollbar_disponible=canvas_barra is not None,
        )
        return None
    medidor = MedidorScrollInicio(inicio, canvas_contenido, scrollbar, canvas_barra)
    inicio._diagnostico_scroll_inicio = medidor
    registrar(
        "dashboard_scroll_instrumentacion",
        pantalla="Inicio / Dashboard / CTkScrollableFrame",
        frame=str(inicio),
        canvas_contenido=str(canvas_contenido),
        scrollbar=str(scrollbar),
        canvas_scrollbar=str(canvas_barra),
        variante=getattr(inicio, "_diagnostico_scrollbar_variante", "ctk"),
        bindings_aditivos=True,
    )
    return medidor


def configurar_variante_scroll_inicio(inicio):
    """Selecciona ctk (predeterminado) o ttk para el scrollbar de Inicio.

    La variante ttk solo se activa con el diagnóstico habilitado y cambia
    únicamente el widget de scrollbar; Canvas, contenido y scrollregion se
    conservan. Reiniciar con CALCULADORA_INICIO_SCROLLBAR=ctk revierte B.
    """
    if not ACTIVO:
        return "ctk"
    variante = os.environ.get("CALCULADORA_INICIO_SCROLLBAR", "ctk").strip().lower()
    if variante not in {"ctk", "ttk"}:
        registrar(
            "dashboard_scroll_variante_invalida",
            pantalla="Inicio / Dashboard / CTkScrollableFrame",
            valor=variante,
            variante_activa="ctk",
        )
        variante = "ctk"
    if getattr(inicio, "_diagnostico_scrollbar_variante", None) is not None:
        return inicio._diagnostico_scrollbar_variante

    inicio._diagnostico_scrollbar_variante = "ctk"
    inicio._diagnostico_scrollbar_activo = inicio._scrollbar
    if variante == "ttk":
        from tkinter import ttk

        scrollbar_ctk = inicio._scrollbar
        canvas = inicio._parent_canvas
        master = scrollbar_ctk.master
        grid = scrollbar_ctk.grid_info()
        opciones_grid = {
            clave: grid[clave]
            for clave in ("row", "column", "rowspan", "columnspan", "sticky",
                          "padx", "pady", "ipadx", "ipady")
            if clave in grid
        }
        scrollbar_ctk.grid_remove()
        scrollbar_ttk = ttk.Scrollbar(
            master, orient="vertical", command=canvas.yview
        )
        scrollbar_ttk.grid(**opciones_grid)
        canvas.configure(yscrollcommand=scrollbar_ttk.set)
        inicio._diagnostico_scrollbar_activo = scrollbar_ttk
        inicio._diagnostico_scrollbar_variante = "ttk"

    registrar(
        "dashboard_scroll_variante",
        pantalla="Inicio / Dashboard / CTkScrollableFrame",
        variante=inicio._diagnostico_scrollbar_variante,
        canvas_conservado=str(inicio._parent_canvas),
        contenido_conservado=True,
    )
    return inicio._diagnostico_scrollbar_variante


def registrar_configure(contenedor, origen):
    """Captura un Configure, conservando una única llamada al ajuste original."""
    medidor = getattr(contenedor, "_diagnostico_scroll", None)
    if medidor is None:
        contenedor._actualizar()
    else:
        medidor.configure(origen)


def instalar_raiz(raiz):
    if not ACTIVO or getattr(raiz, "_diagnostico_configure_instalado", False):
        return
    raiz._diagnostico_configure_instalado = True
    raiz._diagnostico_configure_total = 0

    def contar(evento):
        raiz._diagnostico_configure_total += 1

    raiz.bind_all("<Configure>", contar, add="+")


def medir_navegacion(metodo):
    """Decorador optativo: tiempos, árboles Tk y eventos Configure de la raíz."""
    @wraps(metodo)
    def envoltura(self, *args, **kwargs):
        if not ACTIVO:
            return metodo(self, *args, **kwargs)
        inicio = time.perf_counter()
        try:
            antes = contar_widgets(self)
            configures_antes = getattr(self, "_diagnostico_configure_total", 0)
            resultado = metodo(self, *args, **kwargs)
            despues = contar_widgets(self)
            registrar(
                "navegacion_funcion",
                funcion=metodo.__name__,
                modulo_activo=getattr(self, "modulo_activo", None),
                modulos_retenidos=len(getattr(self, "paneles", {})),
                widgets_antes=antes,
                widgets_despues=despues,
                diferencia_widgets=despues - antes,
                configures=getattr(self, "_diagnostico_configure_total", 0) - configures_antes,
                duracion_ms=(time.perf_counter() - inicio) * 1000,
            )
            return resultado
        except Exception as error:
            registrar("navegacion_error", funcion=metodo.__name__, error=repr(error))
            raise
    return envoltura
