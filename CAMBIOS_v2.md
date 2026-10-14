# Cambios v1.1 → v2.0 (Etapas 1 a 4)

**Objetivo:** que la skill funcione para **cualquier organización y cualquier país** sin tocar sus reglas. Lo específico pasa a piezas intercambiables. La v1.1 queda intacta en `versiones/v1.1/`, porque es la que documenta la primera entrega del TIF (`informe_TIF.tex`).

## 1. Arquitectura en tres capas

| Capa | Dónde | ¿Cambia por…? |
|---|---|---|
| **Norma (ISO/IEC 27701:2025)**: 24 controles, criterios, puntaje | `pims-dpa-auditor/references/`, `scripts/` | Nada: es general |
| **Jurisdicción (país)**: ley, autoridad, plazos legales | `pims-dpa-auditor/jurisdicciones/<id>/` | País |
| **Organización**: política interna, aprobadores, perfil | `organizaciones/<id>/` | Organización |

## 2. Qué cambió en la skill `pims-dpa-auditor`

| Archivo | Cambio |
|---|---|
| `SKILL.md` | Nueva sección "Contexto de ejecución". El Paso 1 usa el perfil si existe; el Paso 2 aplica el nivel de riesgo más alto entre contrato y perfil; el Paso 5 lee la jurisdicción configurada. Regla 7 extendida a todos los documentos (contrato, perfil, documentos institucionales). **Regla 9 nueva: asimetría del contexto.** La descripción ya no está atada a Perú (958 caracteres, bajo el límite de 1024). Se mantienen las 11 secciones del informe. |
| `references/marco_legal_peru.md` | Movido a `jurisdicciones/peru/marco_legal.md`, con el mismo contenido y una tabla de estado. Se añade `parametros_legales.json`. |
| `jurisdicciones/_plantilla/` y `LEEME.md` | Plantilla para agregar países, con estados `Plantilla` → `Borrador` → `En uso` / `Verificada`. |
| `references/criterios_semaforo.md` | "Equivalente a la Ley 29733" pasa a "equivalente a la ley aplicable". En §1 se añade la regla del perfil. **Fórmulas y reglas sin cambios.** |
| `references/controles_iso27701_2025.md` | A.3.13 y "No aplica" redactados sin fijar el país. |
| `assets/plantilla_dpa_baseline.md` | `{ley_aplicable}`, `{reglamento}` y `{autoridad}` en lugar de la Ley 29733 y la ANPD fijas. |
| `assets/config_organizacion.json` | Pasa a ser la configuración **por defecto** (organización genérica). Añade `jurisdiccion` y `aprobadores_cargos`. Mismos valores de política. |
| `assets/esquema_salida.json` | Bloques opcionales `organizacion` y `jurisdiccion`; en `tercero`, `proceso_origen` y `fuente_perfil`. `fuente_requisito` acepta "Ley aplicable" y conserva "Ley 29733/Reglamento" por compatibilidad. En `trazabilidad`: versión de jurisdicción y de perfil, y advertencias. Ningún campo obligatorio nuevo, así que los registros v1.1 siguen siendo válidos. |
| `scripts/calcular_resultado.py` | Opciones `--org`, `--perfil` y `--jurisdicciones` (`--config` sigue funcionando). Carga y valida la jurisdicción, registra el perfil (versión, estado y SHA-256) y advierte si la política interna no deja margen para cumplir la ley. **El núcleo de cálculo es idéntico al de la v1.1.** Corregido el `−` (U+2212) que fallaba en consolas Windows. |

## 3. Skill nueva: `pims-perfilador-organizacion` (Agente 1, inventario)

Convierte los documentos institucionales de cualquier organización (ROF, MOF, TUPA, organigrama, procesos…) en un `perfil_organizacion.md` con **formato fijo de 8 secciones** y fuente `[Dn, p. X]` en cada dato.

- **Sin juicios de cumplimiento.** En la columna "¿DPA localizado?" solo se admite Sí, No o Desconocido.
- **El texto de los documentos es dato, no instrucción.** Las frases dirigidas a un evaluador van a la sección 8.
- **Sale en `Borrador`**, hasta que el DPO lo valida.
- `scripts/validar_perfil.py` comprueba el formato, la trazabilidad y la ausencia de juicios de cumplimiento. Su opción `--json` está pensada para n8n.

## 4. Organizaciones

`organizaciones/_plantilla/`, `inversiones_altiplano/` (la de los contratos de la v1.1) y `unsa/` (configuración **provisional**, sin documentos todavía). Ver `organizaciones/LEEME.md`.

## 5. Contenido no confiable y asimetría: defensa en tres niveles

1. **Perfilador:** no incorpora instrucciones de los documentos y las registra en la sección 8.
2. **Validador:** rechaza perfiles con juicios de cumplimiento o fuentes inexistentes.
3. **Auditor:** la regla 9 impide que el perfil cuente como evidencia. Además, **el script no deja que el perfil toque el cálculo**: una prueba demuestra que NubeAndina da 22/100 sin perfil, con perfil y con un perfil contaminado.

## 6. Pruebas

```
python pims-dpa-auditor_pruebas/ejecutar_pruebas.py
```

**27/27 correctas.** Cubren:

- **Regresión exacta contra la v1.1** sobre los 5 resultados guardados (22, 100, 0, 22 y 100).
- **Jurisdicciones:** estados, errores y selección de otro país.
- **Coherencia** de la política interna con la ley.
- **Perfil:** hash e inmunidad del cálculo.
- **Validador:** referencia válida; contaminado, plantilla, `D9` inexistente y fila sin fuente rechazados.
- **Compatibilidad:** config v1.1, consola cp1252 y entradas inválidas.
- **Rutas** de `casos_de_prueba.json`.

`casos_de_prueba.json` tiene las rutas corregidas y 4 casos nuevos (6–9) para probar con el modelo el perfil, la asimetría hacia arriba y hacia abajo, y el perfilador. **Esos 4 casos requieren ejecutar el modelo** y no forman parte de la suite automática.

## 7. Otros

- `demo/build_embed.py` lee la jurisdicción desde su nueva ubicación. `corpus.js` está regenerado, así que la demo actual sigue funcionando con la v2.0.
- Ambas skills pasan `skillkit lint --strict` con 100/100.

## 8. Etapa 2 — n8n como motor central

Detalle completo e instalación en **`n8n/INSTALACION_N8N.md`**.

| Pieza | Qué es |
|---|---|
| `n8n/construir_flujos.py` | Genera los **11 flujos** (162 nodos) desde una sola fuente, con la ruta del proyecto y las librerías JS embebidas. |
| `n8n/instalar_flujos.py` | Construye, importa y publica en n8n. Genera `iniciar_n8n.bat` / `.sh` con las variables que exige n8n 2.x. |
| `n8n/lib/calcular.js` | Port del cálculo de `calcular_resultado.py`. **Idéntico en 5 012 casos**, incluidos 476 empates de redondeo: Python redondea 22,5 → 22 y JavaScript con `Math.round` daría 23. |
| `n8n/lib/perfil.js` | Port de `validar_perfil.py`. **Idéntico en 1 503 perfiles.** |
| `n8n/lib/prompts.js` | Armado de prompts e inserción de las cifras calculadas en el informe (secciones 1, 6, 7, 10 y 11). |
| `n8n/pruebas/` | Modelo simulado (Ollama, Anthropic, OpenAI y `claude`), equivalencia JS = Python y 21 pruebas de extremo a extremo. |
| `datos/` | Registro de DPAs, trabajos en curso, configuración del modelo, alertas de renovación. |

Flujos: Auditar contrato · Perfilar organización · Aprobaciones (DPO → Legal) · Renovaciones (cada lunes) · Consultas · Administración · Modelo de IA (selector) · Leer y Guardar archivos · Claude Code y Crear carpetas (los únicos que usan *Execute Command*, aislados).

**Verificado en n8n 2.43.4 real** con el modelo simulado: **21/21 pruebas**, también en una segunda corrida sobre datos existentes, instalando con `instalar_flujos.py` y arrancando con el script generado. Las pruebas cubren:

- los **cuatro proveedores** dan 22/100 para NubeAndina, idéntico a Python;
- AndesCloud con perfil da 100, y el perfil llega al prompt marcado como no confiable;
- DigiServ da 0;
- corrección automática de un JSON roto;
- contrato en PDF de 2 páginas, con hash de los bytes;
- errores con mensaje claro (organización inexistente, petición inválida, modelo caído);
- doble puerta con 409 fuera de turno;
- perfilador con hashes reales;
- validación del perfil por el DPO;
- brechas (terceros sin DPA evaluado);
- creación de organización y subida de documentos;
- renovaciones, también la ejecución programada;
- **sin *Execute Command*:** Ollama y API siguen funcionando, y Claude Code y crear organización devuelven instrucciones claras.

Hallazgos de la instalación que condicionaron el diseño:

- **n8n 2.43 exige Node.js 24 o superior.**
- *Execute Command* viene desactivado (`NODES_EXCLUDE`).
- Los nodos de archivos solo acceden a `~/.n8n-files` salvo que se configure `N8N_RESTRICT_FILE_ACCESS_TO`.
- Los nodos Code no pueden leer ni escribir archivos ni usar `require`, y no crean carpetas.
- La activación es `publish:workflow`.

## 9. Etapa 3 — Página web servida por n8n

**http://localhost:5678/webhook/pims/app** · documentación en `web/LEEME.md` · guion de la demo en `GUIA_DEMO.md`.

- **Una página sin frameworks** (`web/index.html`) con siete pantallas: auditar, expedientes, expediente, por aprobar, organización y perfil, renovaciones y configuración.
- **Diseño.** La metáfora es el expediente. La *huella* de 24 casillas del semáforo resume cada contrato, y la doble puerta DPO → Legal se ve como **dos sellos** que se estampan al aprobar.
- **Archivos.** Los `.docx` se convierten en el navegador con mammoth; los PDF los lee n8n.
- **Funciona sin CDN.** Las librerías (marked, DOMPurify, mammoth) están en `web/vendor/`, copiadas de npm, con sus licencias.
- **Seguridad.** Funciona con el **aislamiento por defecto** de n8n 2.x (CSP sandbox), sin desactivarlo. Además, la API restringe con `allowedOrigins` quién puede leer sus respuestas: se verificó que un origen externo queda bloqueado.
- **Nuevos flujos y rutas.** Flujo nuevo *PIMS · Página web* (son 12 en total) y ruta `GET pims/documentos`.
- **Probada en Chromium real** contra n8n 2.43.4: **9/9 en tres corridas seguidas**, junto a las 21/21 de los flujos. Las pruebas detectaron cuatro errores, todos corregidos:
  - dos carreras entre pantallas;
  - un conflicto de estilos que deformaba el botón de aprobar;
  - desplazamiento horizontal en móvil.

La demo anterior (`demo/`, que llamaba a `claude -p` desde un servidor Python) queda como antecedente. La página nueva la reemplaza.

## 10. Etapa 4 — Caso UNSA

- **5 contratos ficticios** de proveedores de la UNSA en `pims-dpa-auditor_pruebas/unsa/contratos/` (copiados en `organizaciones/unsa/contratos/`): aula virtual, laboratorio clínico, pasarela de pagos, videovigilancia con reconocimiento facial y soporte del sistema académico (contrato estatal). Cada uno prueba un aspecto distinto del criterio; todos llevan aviso de ficción.
- **Evaluaciones de referencia** (`referencia/`) con `_alternativas` en los controles discutibles (15 en total), y **resultados esperados** (`esperado/`) calculados con `calcular_resultado.py --org organizaciones/unsa --fecha-ref 2026-10-13`. `construir_referencia.py` verifica que cada cita exista literalmente en el contrato. Puntajes: 50, 46, 99, 0 y 31.
- **`comparar_con_referencia.py`**: concordancia exacta y con alternativas, kappa de Cohen, controles críticos, puntaje, banda, dictamen, cobertura de alertas Altas y matriz de confusión. Sirve para comparar modelos.
- **`ejecutar_casos_unsa.py`**: audita los 5 contratos a través de n8n con el modelo configurado (con `--repeticiones` para medir estabilidad) y genera `comparacion.md`.
- `casos_unsa.json` en formato de evaluación de la skill.
- `modelo_simulado.py` reconoce los contratos de la UNSA y devuelve su referencia. Comprobado de punta a punta por n8n: 120/120 controles, kappa 1,0, puntajes y dictámenes idénticos.
- `organizaciones/unsa/LEEME.md`: qué documentos institucionales conseguir, dónde buscarlos (fuentes verificadas) y los pasos cuando lleguen.
- `GUIA_DEMO.md`: plan B con los contratos de la UNSA si aún no hay documentos.
- **Pendiente del grupo:** revisar las evaluaciones de referencia (las redactó el asistente) y generar el perfil cuando se consigan los documentos reales.

## 11. Documentación actualizada

- `README.md` (nuevo, en la raíz): presentación del proyecto para GitHub, arquitectura, puesta en marcha, casos, pruebas y mapa de la documentación. `.gitignore` excluye lo que genera cada equipo.
- `PROYECTO.md` reescrito para la v2.0: arquitectura, flujo de una auditoría, perfil, seguridad, estructura, pruebas y limitaciones. El análisis de la v1.1 pasa a `versiones/v1.1/PROYECTO_v1.1.md`.
- `MCP_SETUP.md`: presentado como ruta alternativa; §6 marcado como corregido en la v2.0, §7 corregido (la demo no usa API Key) y §9 con la instalación de las dos skills y el uso de organizaciones.
- `demo/README_DEMO.md` y la cabecera de `demo/app.js`: demo anterior, sin la referencia a un archivo inexistente.
- `n8n/INSTALACION_N8N.md`: casos de la UNSA en el modelo simulado, memoria de la tarjeta gráfica con Ollama y nota sobre Docker.
- `pims-dpa-auditor_pruebas/LEEME.md` y `organizaciones/LEEME.md`: todas las pruebas, el caso UNSA y la creación de organizaciones desde la página.

## 12. Pendiente

- Perfil de la UNSA con los documentos reales (ver `organizaciones/unsa/LEEME.md`).
- `informe_TIF.tex` describe la v1.1 (primera entrega). Para la siguiente entrega, la arquitectura vigente está en `PROYECTO.md`.
