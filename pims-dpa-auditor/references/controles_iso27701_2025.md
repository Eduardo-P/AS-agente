# Lista de verificación — ISO/IEC 27701:2025 aplicada a contratos de encargo · v2.1

> **Nota de uso.** Los textos son paráfrasis propias con fines de evaluación; no reproducen la norma. Identificadores, títulos y agrupación en secciones están **verificados contra el texto oficial de ISO/IEC 27701:2025** (Anexo A: Tabla A.1 responsables, Tabla A.2 encargados, Tabla A.3 controles de seguridad compartidos). Los puntos "Guía" resumen, para los controles donde más ayuda a calificar, la guía de implementación del Anexo B en lo que se refleja en un contrato. La columna "Equiv. 2019" ayuda a leer DPAs o certificados antiguos; se dedujo por correspondencia de numeración y sigue **pendiente de verificar contra el Anexo F**.

**Ámbito:** 🅰 = propio del Agente 7 (Terceros). El resto se evalúa como insumo para el Agente 3 (SoA).

## Contenido
1. Control marco del Responsable (A.1.2.7)
2. Tabla A.2 — Encargados (18 controles)
3. Tabla A.3 — Controles compartidos relevantes para el DPA
4. Cómo aplicar "No aplica"

---

## 1. Control marco del Responsable

| Control | Título | Por qué importa |
|---|---|---|
| A.1.2.7 🅰 | Contratos con encargados | Es la obligación de **tu** organización: tener contrato escrito con cada encargado que aborde los controles de la Tabla A.2. Guía (B.1.2.7): por defecto todos los controles de la Tabla A.2 se consideran pertinentes; excluir uno exige justificarlo. Toda la evaluación sirve para demostrar este control en tu PIMS. |

---

## 2. Tabla A.2 — Controles para encargados

### A.2.2 Condiciones de recolección y tratamiento

**A.2.2.2 — Acuerdo con el cliente** (Equiv. 2019: B.8.2.1)
- Qué debe exigir el DPA: que el encargado trate datos solo según instrucciones documentadas del responsable, y que el contrato defina cómo el encargado ayudará al responsable a cumplir sus obligaciones (derechos de titulares, evaluaciones de impacto, incidentes).
- Guía (B.2.2.2): el contrato debería cubrir la asistencia del encargado en privacidad desde el diseño, seguridad del tratamiento, notificación de brechas (a la autoridad, al responsable y a los titulares), evaluaciones de impacto y consultas previas a la autoridad. Algunas leyes exigen además objeto, duración, naturaleza y finalidad del tratamiento, tipos de datos y categorías de titulares.
- Señales de incumplimiento: objeto y finalidad del tratamiento indefinidos; ausencia de anexo con categorías de datos/titulares; instrucciones "según el criterio del proveedor".

**A.2.2.3 — Fines de la organización** (Equiv. 2019: B.8.2.2)
- Qué debe exigir: tratamiento limitado a los fines indicados por el responsable.
- Guía (B.2.2.3): el contrato fija el objetivo y el plazo del servicio; el responsable puede verificar que se respeta la limitación de fines, también por los sub-encargados.
- Señales: el proveedor puede usar datos para "mejorar sus servicios", "analítica propia", entrenar modelos, o fines no definidos. → Riesgo alto: el proveedor podría convertirse en responsable.

**A.2.2.4 — Uso para marketing y publicidad** (Equiv. 2019: B.8.2.3)
- Qué debe exigir: prohibición de usar los datos para marketing o publicidad sin consentimiento válido obtenido por el responsable; el encargado no puede condicionar el servicio a ese consentimiento.
- Señales: silencio total sobre marketing; permisos genéricos de "uso comercial".

**A.2.2.5 — Instrucción infractora** (Equiv. 2019: B.8.2.4)
- Qué debe exigir: deber del encargado de avisar al responsable si considera que una instrucción vulnera la ley aplicable.
- Señales: cláusula ausente.

**A.2.2.6 — Obligaciones del cliente** (Equiv. 2019: B.8.2.5)
- Qué debe exigir: que el encargado entregue información suficiente para que el responsable demuestre cumplimiento (derecho de auditoría o inspección, informes de terceros, cuestionarios).
- Guía (B.2.2.6): incluye si el encargado permite y colabora con auditorías hechas por el responsable o por un auditor designado o acordado con él.
- Señales: sin derecho de auditoría; auditoría solo "a discreción del proveedor"; costos prohibitivos.

**A.2.2.7 — Registros del tratamiento** (Equiv. 2019: B.8.2.6)
- Qué debe exigir: que el encargado mantenga registros del tratamiento realizado por cuenta del responsable.
- Señales: cláusula ausente.

### A.2.3 Obligaciones con los titulares

**A.2.3.2 — Cumplimiento de obligaciones con los titulares** (Equiv. 2019: B.8.3.1)
- Qué debe exigir: medios y plazos para que el encargado asista al responsable con solicitudes de derechos (acceso, rectificación, cancelación, oposición — ARCO — y portabilidad); reenvío al responsable de solicitudes recibidas directamente.
- Guía (B.2.3.2): si el responsable depende del encargado (información o medidas técnicas, p. ej. rectificar o eliminar a tiempo), eso debe quedar especificado en el contrato.
- Señales: sin plazo de asistencia; el proveedor responde directamente a titulares sin instrucción.

### A.2.4 Privacidad desde el diseño y por defecto

**A.2.4.2 — Archivos temporales** (Equiv. 2019: B.8.4.1)
- Qué debe exigir: eliminación de archivos temporales con datos personales en un período definido y documentado.
- Señales: cláusula ausente (control no crítico: su ausencia es ⚪ Sin evidencia).

**A.2.4.3 — Devolución, transferencia o eliminación de datos** (Equiv. 2019: B.8.4.2)
- Qué debe exigir: al terminar el contrato, devolver o eliminar los datos (incluidas copias y respaldos) en un plazo definido, con constancia/certificado de eliminación; política de eliminación disponible para el responsable.
- Guía (B.2.4.3): la eliminación alcanza al encargado **y a sus sub-encargados**, en todo lugar donde estén los datos, incluidos respaldos y copias de continuidad. La política de eliminación debe estar disponible para el responsable a su pedido e indicar cuánto se conservan los datos tras el término (para evitar pérdidas por un vencimiento accidental).
- Señales: "plazo razonable"; conservación indefinida de respaldos; sin certificado; la obligación no alcanza a los sub-encargados.

**A.2.4.4 — Controles de transmisión** (Equiv. 2019: B.8.4.3)
- Qué debe exigir: protección de los datos transmitidos por redes (p. ej. cifrado en tránsito) para que lleguen al destino previsto.
- Señales: sin mención a cifrado ni medidas de transmisión.

### A.2.5 Compartición, transferencia y comunicación

**A.2.5.2 — Base para transferencias entre jurisdicciones** (Equiv. 2019: B.8.5.1)
- Qué debe exigir: informar al responsable de las bases y mecanismos de transferencia internacional y de cambios en ellos, con posibilidad de objetar o resolver.
- Guía (B.2.5.2): informar de toda transferencia (a proveedores, a otras partes, a otros países u organismos internacionales) y de los cambios **con antelación y en un plazo acordado**; identificar el mecanismo (cláusulas modelo, normas corporativas vinculantes, reglas transfronterizas). Si el contrato permite cambios sin aviso, debe fijar sus límites.
- Señales: transferencias permitidas "a cualquier país donde opere el proveedor".

**A.2.5.3 — Países y organizaciones internacionales destino** (Equiv. 2019: B.8.5.2)
- Qué debe exigir: lista concreta de países a los que pueden transferirse los datos.
- Guía (B.2.5.3): la lista incluye los países de los sub-encargados.
- Señales: lista ausente o abierta.

**A.2.5.4 — Registros de comunicaciones a terceros** (Equiv. 2019: B.8.5.3)
- Qué debe exigir: registro de comunicaciones de datos a terceros (qué, a quién, cuándo).
- Señales: cláusula ausente.

**A.2.5.5 — Notificación de solicitudes de comunicación** (Equiv. 2019: B.8.5.4)
- Qué debe exigir: avisar al responsable de solicitudes legalmente vinculantes de comunicación (p. ej. autoridades), salvo prohibición legal.
- Señales: cláusula ausente.

**A.2.5.6 — Comunicaciones legalmente vinculantes** (Equiv. 2019: B.8.5.5)
- Qué debe exigir: rechazar solicitudes no vinculantes, consultar al responsable antes de comunicar, aceptar solo las legalmente vinculantes.
- Señales: el proveedor puede entregar datos "a requerimiento de cualquier autoridad" sin aviso.

**A.2.5.7 🅰 — Divulgación de subcontratistas** (Equiv. 2019: B.8.5.6)
- Qué debe exigir: lista de sub-encargados (nombre, servicio, país) antes de su uso.
- Señales: sin lista; lista "disponible en la web" sin compromiso de vigencia.

**A.2.5.8 🅰 — Contratación de subcontratistas** (Equiv. 2019: B.8.5.7)
- Qué debe exigir: contratar sub-encargados solo conforme al contrato (autorización específica o general) y mediante contrato escrito que les imponga obligaciones equivalentes.
- Guía (B.2.5.6): el cambio de sub-encargado requiere autorización escrita del responsable antes de que trate datos (cláusula del contrato o acuerdo puntual).
- Señales: autorización general sin condiciones; sin obligaciones en cascada.

**A.2.5.9 🅰 — Cambio de subcontratista** (Equiv. 2019: B.8.5.8)
- Qué debe exigir: aviso previo de cambios de sub-encargados con plazo para objetar.
- Señales: cambios sin aviso o con aviso posterior.

---

## 3. Tabla A.3 — Controles compartidos relevantes para el DPA

Solo se listan los que se reflejan normalmente en un contrato. Califícalos con el mismo semáforo.

| Control | Título (paráfrasis) | Qué buscar en el DPA |
|---|---|---|
| A.3.9 | Derechos de acceso | Acceso a datos limitado a personal autorizado y con necesidad; deber de confidencialidad del personal. |
| A.3.10 🅰 | Seguridad en acuerdos con proveedores | Que el contrato fije las **medidas técnicas y organizativas mínimas**, reparta responsabilidades entre las partes, prevea cumplimiento auditado de forma independiente e incluya la notificación de incidentes con plazos. Guía (B.3.10): si el proveedor es encargado, sus propios proveedores solo tratan los datos según sus instrucciones. |
| A.3.11 | Planificación de gestión de incidentes | Compromiso del encargado de tener procedimiento de incidentes que incluya identificar y registrar brechas de datos personales y notificarlas a quien corresponda, con sus plazos (B.3.11). |
| A.3.12 | Respuesta a incidentes | Guía para encargados (B.3.12): el contrato debe regular la notificación de brechas, cómo el encargado entregará la información que el responsable necesita para notificar a la autoridad, y los plazos de respuesta (sin demora indebida). Contenido del aviso: contacto, descripción y consecuencias probables, número de personas y registros afectados, medidas tomadas o previstas; registro del incidente y cooperación posterior. |
| A.3.13 | Requisitos legales y contractuales | Identificación de la ley aplicable (la de la jurisdicción configurada para la organización; p. ej. Ley 29733 en Perú) y compromiso de cumplirla. |
| A.3.15 | Revisión independiente | Disponibilidad de auditorías o certificaciones de terceros independientes. Guía (B.3.15): si las auditorías individuales del cliente no son prácticas, el encargado entrega, antes de firmar y durante el contrato, evidencia independiente (p. ej. una auditoría) que cubra lo que el cliente necesita y con resultados transparentes. |

> **A.3.14 vs A.3.15.** Son controles distintos: A.3.14 (protección de registros) corresponde al Agente 4 (Evidencia y Auditoría); A.3.15 (revisión independiente) es el que se usa aquí para auditorías del proveedor.

> El **plazo** de aviso de incidentes no lo fija ISO 27701: se toma de la ley aplicable (`jurisdicciones/<id>/`) y de la política interna (`config_organizacion.json` de la organización).

---

## 4. Cómo aplicar "No aplica" (➖)
Marca ➖ solo si el control es imposible por la naturaleza del servicio y lo justificas (p. ej. A.2.5.3 cuando el contrato prohíbe expresamente toda transferencia fuera del país del Responsable y no hay sub-encargados). La ausencia de cláusula **nunca** es "No aplica".
