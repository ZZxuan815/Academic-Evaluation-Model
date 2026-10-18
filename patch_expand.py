from pathlib import Path
p=Path('expand_sr.py');s=p.read_text(encoding='utf-8-sig')
s=s.replace('for a in extra:v.append',"v[9]=('precision','n.','/prɪˈsɪʒən/','数值精度','the level of numerical detail used to represent a value','precise (adj.); precisely (adv.)','numerical precision; reduced precision','exactness; imprecision (opposite)','II-C Quantization and Model Compression','Lower precision can reduce memory requirements.','We checked whether reduced precision affected the answers.')\nfor a in extra:v.append")
s=s.replace("for p in d.paragraphs:\n if p.text.startswith('*Notes on recording'):p.paragraph_format.page_break_before=True", "remove=False\nfor p in list(d.paragraphs):\n if p.text.startswith('*Notes on recording'):remove=True\n if remove:p._element.getparent().remove(p._element)")
p.write_text(s,encoding='utf-8')
