#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador del entregable PDF para Arquitectura de Software (Semestre 2026-2):
'Diseño de Gestión de Usuarios, Catálogo Botánico y Vinculación de Matera (Versión Simplificada)'
Proyecto Matera Inteligente · SmartPlantBase
"""

import os
import subprocess
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_bg(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=60, bottom=60, left=90, right=90):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def set_row_props(row, is_header=False):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
    if is_header:
        trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

def set_table_borders(table, color="D0D7DE", sz="4"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def set_callout_borders(table, border_color="1B365D", sz="24"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:insideH w:val="none"/>'
        f'<w:insideV w:val="none"/>'
        f'<w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{border_color}"/>'
        f'<w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def set_code_box_borders(table, border_color="D1D5DB", sz="4"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{border_color}"/>'
        f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{border_color}"/>'
        f'<w:insideH w:val="none"/>'
        f'<w:insideV w:val="none"/>'
        f'<w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{border_color}"/>'
        f'<w:right w:val="single" w:sz="{sz}" w:space="0" w:color="{border_color}"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def add_callout(doc, title, paragraphs_content, border_color="1B365D", bg_color="F0F4F8", title_color=None):
    if title_color is None:
        title_color = border_color
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    set_row_props(t.rows[0])
    set_callout_borders(t, border_color=border_color, sz="24")
    cell = t.rows[0].cells[0]
    cell.width = Inches(7.0)
    set_cell_bg(cell, bg_color)
    set_cell_margins(cell, top=70, bottom=70, left=130, right=100)
    
    # Title paragraph
    p0 = cell.paragraphs[0]
    p0.paragraph_format.space_before = Pt(0)
    p0.paragraph_format.space_after = Pt(2)
    p0.paragraph_format.line_spacing = 1.1
    p0.paragraph_format.keep_with_next = True
    r_title = p0.add_run(title)
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(9.5)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor.from_string(title_color)
    
    # Body paragraphs
    for idx, text in enumerate(paragraphs_content):
        p = cell.add_paragraph()
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.1
        if idx < len(paragraphs_content) - 1:
            p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
    
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(2)

def add_code_block(doc, code_text, font_size=8):
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    set_row_props(t.rows[0])
    set_code_box_borders(t, border_color="D1D5DB", sz="6")
    cell = t.rows[0].cells[0]
    cell.width = Inches(7.0)
    set_cell_bg(cell, "F8F9FA")
    set_cell_margins(cell, top=60, bottom=60, left=100, right=80)
    
    lines = code_text.strip().split("\n")
    p0 = cell.paragraphs[0]
    p0.paragraph_format.space_before = Pt(0)
    p0.paragraph_format.space_after = Pt(0)
    p0.paragraph_format.line_spacing = 1.03
    r0 = p0.add_run(lines[0])
    r0.font.name = "Consolas"
    r0.font.size = Pt(font_size)
    r0.font.color.rgb = RGBColor(0x24, 0x29, 0x2E)
    
    for line in lines[1:]:
        p = cell.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.03
        r = p.add_run(line if line.strip() != "" else " ")
        r.font.name = "Consolas"
        r.font.size = Pt(font_size)
        r.font.color.rgb = RGBColor(0x24, 0x29, 0x2E)
        
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(2)

def build_document():
    doc = docx.Document()
    
    # Margins: 0.75 in (54 pt)
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)
        
        # Header
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("SmartPlantBase · Arquitectura de Software (Semestre 2026-2) — Universidad Sergio Arboleda")
        hrun.font.name = "Calibri"
        hrun.font.size = Pt(8)
        hrun.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
        
        # Footer
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        frun = fp.add_run("Documento de Diseño Arquitectónico · Gestión de Usuarios, Matera y QR · Versión Simplificada")
        frun.font.name = "Calibri"
        frun.font.size = Pt(8)
        frun.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

    COLOR_PRI = RGBColor(0x1B, 0x36, 0x5D)  # Navy Blue
    COLOR_SEC = RGBColor(0x1E, 0x7E, 0x34)  # Botanical Green
    COLOR_DARK = RGBColor(0x22, 0x22, 0x22) # Main text
    COLOR_MUT = RGBColor(0x55, 0x55, 0x55)  # Muted grey
    
    def add_h1(text, keep_next=True):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(9)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = keep_next
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = COLOR_PRI
        return p

    def add_h2(text, keep_next=True):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(7)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = keep_next
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(10.5)
        r.font.bold = True
        r.font.color.rgb = COLOR_SEC
        return p

    def add_body(text, space_after=3, keep_next=False):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.12
        p.paragraph_format.keep_with_next = keep_next
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)
        r.font.color.rgb = COLOR_DARK
        return p

    # =============================================================
    # ENCABEZADO Y TÍTULO
    # =============================================================
    p_inst = doc.add_paragraph()
    p_inst.paragraph_format.space_before = Pt(0)
    p_inst.paragraph_format.space_after = Pt(1)
    r_inst = p_inst.add_run("UNIVERSIDAD SERGIO ARBOLEDA — ESCUELA DE CIENCIAS EXACTAS E INGENIERÍA\n")
    r_inst.font.name = "Calibri"
    r_inst.font.size = Pt(9.5)
    r_inst.font.bold = True
    r_inst.font.color.rgb = COLOR_PRI
    
    r_sub = p_inst.add_run("Ingeniería de Sistemas y Computación · Asignatura: Arquitectura de Software · 2026-2")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(9)
    r_sub.font.color.rgb = COLOR_MUT
    
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(6)
    p_title.paragraph_format.space_after = Pt(2)
    r_tit = p_title.add_run("Diseño de Gestión de Usuarios, Catálogo Botánico y Vinculación de Matera")
    r_tit.font.name = "Calibri"
    r_tit.font.size = Pt(16)
    r_tit.font.bold = True
    r_tit.font.color.rgb = COLOR_PRI
    
    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_before = Pt(0)
    p_meta.paragraph_format.space_after = Pt(4)
    r_m1 = p_meta.add_run("Proyecto Matera Inteligente · SmartPlantBase ")
    r_m1.font.name = "Calibri"
    r_m1.font.size = Pt(9.5)
    r_m1.font.bold = True
    r_m1.font.color.rgb = COLOR_SEC
    
    r_m2 = p_meta.add_run("| Versión Simplificada y Defendible (Anti-Overengineering)\n")
    r_m2.font.name = "Calibri"
    r_m2.font.size = Pt(9)
    r_m2.font.color.rgb = COLOR_MUT
    
    r_m3 = p_meta.add_run("Autor: Esteban (Ingeniería de Sistemas) · Soporte: College Agent · Fecha: Septiembre 2026")
    r_m3.font.name = "Calibri"
    r_m3.font.size = Pt(8.5)
    r_m3.font.color.rgb = COLOR_MUT

    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_before = Pt(0)
    p_div.paragraph_format.space_after = Pt(6)
    r_div = p_div.add_run("―" * 68)
    r_div.font.size = Pt(8)
    r_div.font.color.rgb = COLOR_SEC

    # =============================================================
    # SECCIÓN 1: ENFOQUE Y PROPÓSITO
    # =============================================================
    add_h1("1. Enfoque y Propósito del Documento")
    add_body(
        "El objetivo fundamental de este documento es definir un modelo arquitectónico claro, directo y libre "
        "de sobreingeniería para satisfacer tres necesidades operativas esenciales del ecosistema SmartPlantBase:\n"
        "1. Gestión Segura de Usuarios y Catálogo: Definir roles claros que garanticen la curaduría agronómica "
        "y protejan la base de conocimientos botánicos de datos caóticos o ficticios.\n"
        "2. Precisión Conceptual de la Tríada: Modelar con rigurosidad la diferencia entre el hardware reutilizable (matera), "
        "el organismo biológico perecedero (planta/mata) y la plantilla taxonómica de referencia (especie).\n"
        "3. Vinculación Física Transparente: Establecer un flujo simple mediante código QR impreso en el hardware, "
        "desacoplado de detalles de firmware o microcontrolador."
    )

    add_callout(
        doc,
        title="CRITERIO DE PROPORCIONALIDAD Y DEFENSA ORAL (ANTI-OVERENGINEERING GATE)",
        paragraphs_content=[
            "Este diseño elimina de raíz abstracciones prematuras que sobrecargaban versiones anteriores: criptografía asimétrica por hardware en microcontroladores, tokens de aprovisionamiento de fábrica a 128 bits, sincronización obligatoria RTC/NTP y particiones NVS en memoria flash.",
            "Criterio Rector: Un estudiante de ingeniería de sistemas debe ser capaz de dibujar este modelo en un tablero y defenderlo con total soltura en 5 minutos ante el docente examinador, demostrando maestría en Clean Architecture y proporcionalidad tecnológica."
        ],
        border_color="1B365D",
        bg_color="F0F4F8"
    )

    # =============================================================
    # SECCIÓN 2: ROLES DEL SISTEMA Y GESTIÓN DE USUARIOS
    # =============================================================
    add_h1("2. Roles del Sistema y Gestión de Usuarios")
    add_body(
        "Para mantener el sistema seguro, conciso y fácil de gobernar, se definen estrictamente dos roles "
        "sin jerarquías intermedias ni roles superfluos:"
    )

    t_roles = doc.add_table(rows=3, cols=4)
    t_roles.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_roles.autofit = False
    set_table_borders(t_roles)
    
    col_w_r = [Inches(1.2), Inches(1.8), Inches(2.2), Inches(1.8)]
    r_hdrs = ["Rol", "Identificador", "Alcance y Responsabilidad", "Capacidades de Especies"]
    set_row_props(t_roles.rows[0], is_header=True)
    for i, h in enumerate(r_hdrs):
        cell = t_roles.rows[0].cells[i]
        cell.width = col_w_r[i]
        set_cell_bg(cell, "1B365D")
        set_cell_margins(cell, top=60, bottom=60, left=70, right=70)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = "Calibri"
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    data_roles = [
        ("Usuario Regular", "USER", "Dueño de sus materas físicas y plantas sembradas. Visualiza diagnósticos y alertas en su dashboard.", "Lectura pública del catálogo. NO puede crear ni editar especies globales."),
        ("Superadministrador", "SUPERADMIN", "Curador agronómico y guardián de la base de datos oficial del sistema.", "ÚNICO facultado para dar de alta nuevas especies botánicas y definir rangos.")
    ]
    for idx, d in enumerate(data_roles, start=1):
        row = t_roles.rows[idx]
        set_row_props(row)
        bg = "F8F9FA" if idx % 2 == 1 else "FFFFFF"
        for c_idx, txt in enumerate(d):
            c = row.cells[c_idx]
            c.width = col_w_r[c_idx]
            set_cell_bg(c, bg)
            set_cell_margins(c, top=50, bottom=50, left=70, right=70)
            p = c.paragraphs[0]
            p.paragraph_format.line_spacing = 1.08
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(txt)
            r.font.name = "Calibri"
            r.font.size = Pt(8.5)
            if c_idx <= 1:
                r.font.bold = True
                r.font.color.rgb = COLOR_PRI
            else:
                r.font.color.rgb = COLOR_DARK

    sp_r = doc.add_paragraph()
    sp_r.paragraph_format.space_before = Pt(1)
    sp_r.paragraph_format.space_after = Pt(3)

    add_h2("2.1 El Usuario Regular (USER)")
    add_body(
        "• Se registra mediante correo electrónico y contraseña (hasheada en almacenamiento seguro con salt).\n"
        "• Es el titular exclusivo de sus materas físicas vinculadas y de las plantas vivas sembradas en ellas.\n"
        "• Puede consultar en cualquier momento la lista de especies botánicas soportadas en la plataforma.\n"
        "• Restricción fundamental de seguridad y dominio: El usuario regular NO puede registrar especies nuevas "
        "en el catálogo oficial de la plataforma."
    )

    add_h2("2.2 El Superadministrador (SUPERADMIN)")
    add_body(
        "• Usuario con privilegios elevados de curaduría agronómica y administración del sistema.\n"
        "• Es el único actor facultado para invocar el endpoint protegido POST /api/v1/especies, creando fichas botánicas oficiales "
        "con sus rangos agronómicos de referencia (humedad %, iluminancia lux, temperatura °C).\n"
        "• Puede corregir o normalizar parámetros ante nuevas publicaciones científicas o calibraciones de campo."
    )

    add_h2("2.3 ¿Por qué es INDISPENSABLE un Superadmin para las Especies?")
    add_body(
        "Esta separación no responde a un capricho administrativo, sino a una decisión crítica de arquitectura de software "
        "que previene dos fallos graves que quebrarían el funcionamiento de la aplicación:"
    )

    add_callout(
        doc,
        title="JUSTIFICACIÓN DE INGENIERÍA: LOS 2 MOTIVOS CENTRALES DEL SUPERADMIN",
        paragraphs_content=[
            "1. Problema del Catálogo Caótico (Fragmentación y Basura): Si los usuarios crearan libremente especies, en cuestión de días la base de datos se llenaría de duplicados desordenados: 'Tomate', 'tomate', 'Tomate cherry', 'tomatico' y 'Solanum lycopersicum'. Cada uno asociado a una matera distinta, haciendo inviable la analítica, las búsquedas cruzadas y la comparativa agronómica entre cultivos.",
            "2. Problema de la Integridad Agronómica y el Motor de Reglas: El valor central de SmartPlantBase reside en su EvaluadorDiagnostico, el cual compara lecturas físicas contra rangos biológicos óptimos. Si un usuario ingresa una especie con límites absurdos (ej. temperatura óptima de 95°C o humedad del 2%), el motor generará diagnósticos fallidos o recomendaciones que ahoguen o sequen la planta. El Superadmin actúa como curador botánico oficial, garantizando la validez agronómica de la plataforma."
        ],
        border_color="B94A04",
        bg_color="FFF8F0",
        title_color="B94A04"
    )

    # =============================================================
    # SECCIÓN 3: LA TRÍADA CLAVE
    # =============================================================
    add_h1("3. Modelo Conceptual: La Tríada Clave")
    add_body(
        "Un error arquitectónico habitual en proyectos IoT es fusionar la matera física con la planta viva "
        "en una sola tabla o entidad. En el dominio real existen tres abstracciones con ciclos de vida totalmente disjuntos:"
    )

    t_triada = doc.add_table(rows=4, cols=5)
    t_triada.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_triada.autofit = False
    set_table_borders(t_triada)
    
    col_w_t = [Inches(1.1), Inches(1.7), Inches(1.4), Inches(1.2), Inches(1.6)]
    t_hdrs = ["Concepto", "¿Qué es en la realidad?", "¿Quién lo administra?", "Identificador", "Ejemplo Práctico"]
    set_row_props(t_triada.rows[0], is_header=True)
    for i, h in enumerate(t_hdrs):
        cell = t_triada.rows[0].cells[i]
        cell.width = col_w_t[i]
        set_cell_bg(cell, "1B365D")
        set_cell_margins(cell, top=60, bottom=60, left=50, right=50)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = "Calibri"
        r.font.size = Pt(8)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    data_triada = [
        ("Especie", "Ficha técnica botánica con rangos agronómicos de supervivencia y bienestar.", "Superadmin", "Nombre botánico único", "Albahaca (Ocimum basilicum), Sansevieria"),
        ("Matera", "Recipiente físico contenedor con circuito electrónico ESP32 empotrado.", "Fabricante / Sistema", "Código QR físico único", "MAT-001, MAT-002, MAT-045"),
        ("Planta / Mata", "Organismo vivo sembrado en la matera con ciclo de vida dinámico.", "Usuario Regular", "ID autogenerado (UUID)", "'Mi Albahaca de la cocina', 'Cactus de sala'")
    ]
    for idx, d in enumerate(data_triada, start=1):
        row = t_triada.rows[idx]
        set_row_props(row)
        bg = "F8F9FA" if idx % 2 == 1 else "FFFFFF"
        for c_idx, txt in enumerate(d):
            c = row.cells[c_idx]
            c.width = col_w_t[c_idx]
            set_cell_bg(c, bg)
            set_cell_margins(c, top=50, bottom=50, left=50, right=50)
            p = c.paragraphs[0]
            p.paragraph_format.line_spacing = 1.08
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(txt)
            r.font.name = "Calibri"
            r.font.size = Pt(8)
            if c_idx == 0:
                r.font.bold = True
                r.font.color.rgb = COLOR_PRI
            else:
                r.font.color.rgb = COLOR_DARK

    sp_t = doc.add_paragraph()
    sp_t.paragraph_format.space_before = Pt(1)
    sp_t.paragraph_format.space_after = Pt(3)

    add_body(
        "Estructura de Relaciones del Modelo:\n"
        "• Usuario (1) posee muchas (*) Materas físicas vinculadas a su cuenta.\n"
        "• Matera (1) contiene (0..1) Planta viva en un momento dado.\n"
        "• Planta (*) es de tipo (1) Especie botánica del catálogo oficial curado."
    )

    add_callout(
        doc,
        title="PREGUNTA CLAVE DE SUSTENTACIÓN ORAL ANTE EL DOCENTE",
        paragraphs_content=[
            "Profesor: '¿Por qué separaron Matera de Planta en entidades y tablas distintas en lugar de tener una sola tabla?'",
            "Respuesta Defensiva del Estudiante: 'Porque la matera es un activo físico de hardware reutilizable, mientras que la planta es un ser biológico perecedero. Si una planta se marchita o el usuario decide cosecharla, retira la tierra y siembra un cactus en la MISMA matera física. Al desacoplarlas, reutilizamos el hardware MAT-001 infinitas veces sin perder el histórico de diagnósticos de la planta anterior y sin tener que dar de baja el hardware del sistema.'"
        ],
        border_color="1E7E34",
        bg_color="F2F9F3",
        title_color="1E7E34"
    )

    # =============================================================
    # SECCIÓN 4: EL ESP32 COMO CAJA NEGRA
    # =============================================================
    add_h1("4. El ESP32: Principio de la Caja Negra")
    add_body(
        "Para evitar reincidir en la sobreingeniería de arquitecturas descartadas, se define de manera rigurosa la frontera del microcontrolador:"
    )

    add_callout(
        doc,
        title="REGLA DE ALCANCE: EL MICROCONTROLADOR COMO CAJA NEGRA",
        paragraphs_content=[
            "En esta etapa de gestión de usuarios, catálogos y vinculación, el ESP32 se trata estrictamente como una caja negra:\n"
            "• Sabemos que es el circuito físico empotrado dentro del plástico de la matera que lee los sensores analógicos y digitales.\n"
            "• NO modelamos en este nivel pines GPIO, rutinas de firmware C++, certificados TLS de silicio, timers FreeRTOS ni calibración de voltajes.\n"
            "• Para el backend de gestión, la matera física se identifica únicamente por su Código QR ('MAT-001'). La telemetría de lecturas "
            "se conectará en su respectivo hito como un adaptador de entrada más, manteniendo la pureza de la arquitectura."
        ],
        border_color="1B365D",
        bg_color="F0F4F8"
    )

    # =============================================================
    # SECCIÓN 5: FLUJO DE VINCULACIÓN CON QR
    # =============================================================
    add_h1("5. Flujo de Vinculación con Código QR")
    add_h2("5.1 Contenido del Código QR Físico")
    add_body(
        "El código QR adhesivo pegado en la carcasa plástica de la matera contiene un identificador simple y legible:\n"
        "• Formato directo texto plano: 'MAT-001'\n"
        "• Formato JSON ligero: {\"matera_id\": \"MAT-001\"}\n"
        "No se requieren esquemas criptográficos asimétricos ni claves secretas de 128 bits para el alcance universitario del proyecto."
    )

    add_h2("5.2 Secuencia de Vinculación Paso a Paso")
    
    t_sec = doc.add_table(rows=6, cols=3)
    t_sec.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_sec.autofit = False
    set_table_borders(t_sec)
    
    col_w_s = [Inches(0.6), Inches(2.6), Inches(3.8)]
    s_hdrs = ["Paso", "Interacción / Endpoint", "Lógica de Negocio y Persistencia"]
    set_row_props(t_sec.rows[0], is_header=True)
    for i, h in enumerate(s_hdrs):
        cell = t_sec.rows[0].cells[i]
        cell.width = col_w_s[i]
        set_cell_bg(cell, "1B365D")
        set_cell_margins(cell, top=60, bottom=60, left=60, right=60)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = "Calibri"
        r.font.size = Pt(8.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    data_sec = [
        ("1", "Escaneo QR en App Web/Móvil", "La cámara decodifica el string 'MAT-001' adherido a la matera física."),
        ("2", "GET /api/v1/materas/MAT-001/disponibilidad", "El backend verifica en BD si MAT-001 existe y si su usuario_id es NULL (está libre). Retorna 200 OK disponible."),
        ("3", "Selección en Interfaz", "El usuario elige la especie del catálogo oficial (ej. 'Albahaca') y le asigna un apodo (ej. 'Albahaca de la Ventana')."),
        ("4", "POST /api/v1/materas/vincular", "Transacción atómica: 1) Asigna matera.usuario_id = usuario_id; 2) Inserta nuevo registro de Planta activa vinculada a la matera y a la especie."),
        ("5", "201 Created & Renderizado", "El backend confirma la vinculación y la app redirige al dashboard con la planta activa en monitoreo.")
    ]
    for idx, d in enumerate(data_sec, start=1):
        row = t_sec.rows[idx]
        set_row_props(row)
        bg = "F8F9FA" if idx % 2 == 1 else "FFFFFF"
        for c_idx, txt in enumerate(d):
            c = row.cells[c_idx]
            c.width = col_w_s[c_idx]
            set_cell_bg(c, bg)
            set_cell_margins(c, top=50, bottom=50, left=60, right=60)
            p = c.paragraphs[0]
            p.paragraph_format.line_spacing = 1.08
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(txt)
            r.font.name = "Calibri"
            r.font.size = Pt(8.5)
            if c_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r.font.bold = True
                r.font.color.rgb = COLOR_PRI
            elif c_idx == 1:
                r.font.bold = True
                r.font.color.rgb = COLOR_SEC
            else:
                r.font.color.rgb = COLOR_DARK

    sp_s = doc.add_paragraph()
    sp_s.paragraph_format.space_before = Pt(1)
    sp_s.paragraph_format.space_after = Pt(3)

    add_h2("5.3 Reglas de Negocio en la Vinculación")
    add_body(
        "1. Matera Inexistente: Si el código QR leído no existe en la base de datos, el backend responde 404 Not Found ('Matera no registrada en el sistema').\n"
        "2. Matera Ocupada: Si la matera ya tiene un usuario_id asignado distinto al usuario autenticado, el sistema rechaza la vinculación con 409 Conflict ('Matera ya vinculada a otro usuario').\n"
        "3. Especie Válida: La especie seleccionada debe existir previamente en el catálogo botánico oficial (EspecieRepository).\n"
        "4. Desvinculación Limpia: Si el usuario desvincula la matera, la planta pasa a estado inactiva (preservando histórico) y el campo matera.usuario_id vuelve a NULL, disponible para otro usuario."
    )

    # =============================================================
    # SECCIÓN 6: ALINEACIÓN CON CLEAN ARCHITECTURE
    # =============================================================
    add_h1("6. Alineación con Clean Architecture (SmartPlantBase)")
    add_body(
        "El diseño respeta plenamente la arquitectura limpia ya implementada en el repositorio SmartPlantBase, "
        "sin alterar el núcleo de reglas de negocio previamente validado:"
    )

    add_code_block(
        doc,
        "src/\n"
        "├── domain/                      # Reglas de negocio puras (Python puro, 0 dependencias externas)\n"
        "│   ├── entities.py              # Invarianza: Se preservan Medicion, Especie, Diagnostico.\n"
        "│   │                            # Nuevas entidades: Usuario, RolUsuario, Matera, Planta.\n"
        "│   ├── rules.py                 # EvaluadorDiagnostico (INTACTO, 0 modificaciones).\n"
        "│   └── repositories.py          # Interfaces: EspecieRepo, UsuarioRepo, MateraRepo, PlantaRepo.\n"
        "├── application/                 # Casos de uso de orquestación\n"
        "│   ├── dtos.py                  # DTOs tipados de entrada y salida.\n"
        "│   └── use_cases.py             # RegistrarUsuario, Autenticar, CrearEspecie, VincularMatera.\n"
        "├── infrastructure/              # Adaptadores de persistencia y drivers\n"
        "│   └── repositories/            # SQLiteRepositories (tablas relacionales livianas).\n"
        "└── presentation/                # Controladores HTTP (Flask)\n"
        "    └── controllers.py           # Rutas públicas y protegidas con sesión de usuario."
    )

    add_h2("6.1 Nuevas Entidades de Dominio (src/domain/entities.py)")
    add_body("Implementadas con dataclasses estándar de Python sin acoplamiento a librerías externas:")

    add_code_block(
        doc,
        "from dataclasses import dataclass\n"
        "from enum import Enum\n"
        "from typing import Optional\n"
        "from datetime import datetime\n\n"
        "class RolUsuario(str, Enum):\n"
        "    USER = \"USER\"\n"
        "    SUPERADMIN = \"SUPERADMIN\"\n\n"
        "@dataclass\n"
        "class Usuario:\n"
        "    id: str\n"
        "    email: str\n"
        "    password_hash: str\n"
        "    nombre: str\n"
        "    rol: RolUsuario = RolUsuario.USER\n"
        "    activo: bool = True\n\n"
        "    def es_superadmin(self) -> bool:\n"
        "        return self.rol == RolUsuario.SUPERADMIN\n\n"
        "@dataclass\n"
        "class Matera:\n"
        "    id: str                  # Código legible: \"MAT-001\"\n"
        "    codigo_qr: str           # String decodificado del QR\n"
        "    usuario_id: Optional[str] = None  # None = Disponible\n\n"
        "    @property\n"
        "    def esta_disponible(self) -> bool:\n"
        "        return self.usuario_id is None\n\n"
        "@dataclass\n"
        "class Planta:\n"
        "    id: str\n"
        "    usuario_id: str\n"
        "    matera_id: str\n"
        "    especie_nombre: str\n"
        "    apodo: str\n"
        "    creada_en: datetime\n"
        "    activa: bool = True"
    )

    add_callout(
        doc,
        title="INVARIANZA DEL NÚCLEO BOTÁNICO (PRINCIPIO ABIERTO/CERRADO)",
        paragraphs_content=[
            "Las clases Medicion, Diagnostico, LimiteFisico y el motor EvaluadorDiagnostico no sufren una sola modificación. "
            "Gracias a Clean Architecture, la incorporación de usuarios, roles y hardware se realiza de manera perimetral "
            "sin alterar la lógica de negocio probada con pruebas unitarias."
        ],
        border_color="1E7E34",
        bg_color="F2F9F3",
        title_color="1E7E34"
    )

    add_h2("6.2 Casos de Uso Clave (src/application/use_cases.py)")
    add_body(
        "1. RegistrarUsuarioUseCase & AutenticarUsuarioUseCase: Registro y validación simple de credenciales con hash seguro.\n"
        "2. CrearEspecieUseCase: Recibe el ID del solicitante; si su rol no es SUPERADMIN, rechaza la operación con PermisoDenegadoError. "
        "Si es superadmin, valida rangos biológicos mediante LIMITES_FISICOS y almacena la nueva ficha en EspecieRepository.\n"
        "3. VincularMateraConQRUseCase: Valida existencia y disponibilidad de la matera, existencia de la especie, "
        "asigna matera.usuario_id y persiste la nueva Planta viva en una sola transacción atómica coordinada.\n"
        "4. ListarPlantasDeUsuarioUseCase: Recupera las plantas activas del usuario autenticado con su estado de telemetría y matera asociada."
    )

    add_h2("6.3 Modelo Relacional Simple en SQLite")
    add_body("Esquema DDL relacional claro, sin complejidades de servidores de bases de datos externos:")

    add_code_block(
        doc,
        "-- Usuarios del sistema\n"
        "CREATE TABLE usuarios (\n"
        "    id TEXT PRIMARY KEY,\n"
        "    email TEXT UNIQUE NOT NULL,\n"
        "    password_hash TEXT NOT NULL,\n"
        "    nombre TEXT NOT NULL,\n"
        "    rol TEXT NOT NULL DEFAULT 'USER',\n"
        "    activo INTEGER NOT NULL DEFAULT 1\n"
        ");\n\n"
        "-- Materas físicas (con hardware ESP32 empotrado)\n"
        "CREATE TABLE materas (\n"
        "    id TEXT PRIMARY KEY,\n"
        "    codigo_qr TEXT UNIQUE NOT NULL,\n"
        "    usuario_id TEXT NULL,\n"
        "    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)\n"
        ");\n\n"
        "-- Plantas vivas de los usuarios\n"
        "CREATE TABLE plantas (\n"
        "    id TEXT PRIMARY KEY,\n"
        "    usuario_id TEXT NOT NULL,\n"
        "    matera_id TEXT NOT NULL,\n"
        "    especie_nombre TEXT NOT NULL,\n"
        "    apodo TEXT NOT NULL,\n"
        "    creada_en TEXT NOT NULL,\n"
        "    activa INTEGER NOT NULL DEFAULT 1,\n"
        "    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),\n"
        "    FOREIGN KEY (matera_id) REFERENCES materas(id)\n"
        ");"
    )

    add_body(
        "Ventajas de Persistencia: SQLite almacena todo el estado en un archivo local autocontenido, facilitando "
        "la reproducibilidad, las pruebas automatizadas y la defensa en vivo del proyecto sin dependencias de infraestructura."
    )

    # Forzar salto antes de la sección de sustentación oral para que quede completa como hoja de defensa
    doc.add_page_break()

    # =============================================================
    # SECCIÓN 7: GUÍA EJECUTIVA DE SUSTENTACIÓN ORAL (HOJA FINAL)
    # =============================================================
    add_h1("7. Guía de Sustentación Oral (5 Minutos en Tablero)")
    add_body(
        "Al sustentar este diseño ante el docente, el estudiante debe dibujar el siguiente esquema en el tablero "
        "y responder con convicción a las cuatro preguntas críticas de arquitectura:"
    )

    add_code_block(
        doc,
        "                     ┌───────────────────────────────┐\n"
        "                     │          SUPERADMIN           │\n"
        "                     └──────────────┬────────────────┘\n"
        "                                    │ Administra exclusivamente\n"
        "                                    ▼\n"
        "┌──────────────┐     posee    ┌──────────┐   es de tipo   ┌───────────────┐\n"
        "│   USUARIO    ├─────────────►│  MATERA  ├───────────────►│    ESPECIE    │\n"
        "│  (Regular)   │              │ (QR Fís) │                │  (Catálogo)   │\n"
        "└──────┬───────┘              └────┬─────┘                └───────────────┘\n"
        "       │                           │\n"
        "       │     siembra y nombra      │\n"
        "       └──────────────────────────►│ PLANTA (Ser vivo: 'Mi Albahaca')\n"
        "                                   └─────────────────────────────",
        font_size=8.5
    )

    add_callout(
        doc,
        title="LAS 4 RESPUESTAS CLAVE PARA LA DEFENSA ORAL ANTE EL DOCENTE",
        paragraphs_content=[
            "1. '¿Por qué un Superadmin para las especies?': Para blindar la integridad agronómica del catálogo. Si cualquier usuario crea especies, se colapsa la base de datos con duplicados inconsistentes ('tomate', 'tomatico', 'Tomate cherry') y valores fuera de la realidad biológica que provocarían fallos graves en el motor de diagnóstico.",
            "2. '¿Por qué Matera no es lo mismo que Planta?': Porque la matera es el hardware físico reutilizable (recipiente y circuito) y la planta es el ser vivo perecedero. Si la planta muere o se retira, la matera física se reutiliza para sembrar otra especie sin perder el histórico de diagnósticos ni tener que dar de baja el hardware.",
            "3. '¿Cómo funciona la vinculación por QR?': El QR contiene únicamente el identificador legible ('MAT-001'). La aplicación valida que esté disponible (usuario_id es NULL), y en una sola transacción asocia la matera al usuario y crea la planta con su especie oficial y apodo.",
            "4. '¿Y dónde queda el ESP32 en este diseño?': El ESP32 es el componente de sensado dentro de la matera. En este nivel de software se trata como una caja negra que se integrará limpiamente como un adaptador de telemetría sin acoplar la gestión de usuarios a complejidades de silicio."
        ],
        border_color="1B365D",
        bg_color="F0F4F8"
    )

    # Save DOCX
    docx_path = "/home/esteban/Documents/COLLEGE/2026-2/ARQUIT/SmartPlantBase/docs/gestion_usuarios_y_matera_simple.docx"
    doc.save(docx_path)
    print("DOCX successfully generated:", docx_path)

if __name__ == "__main__":
    build_document()
