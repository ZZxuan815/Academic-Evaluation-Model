from pathlib import Path
p=Path('close_reading.py');s=p.read_text(encoding='utf-8-sig').replace("('subsidies',","('Taxincentives',")
s=s.replace("norm(anchor) in norm(z['text'])","(norm(anchor)==norm(z['text']) if len(norm(anchor))<=3 else norm(anchor) in norm(z['text']))")
s=s.replace("if not hits:\n    # Locate", "if not hits and len(norm(anchor))>3:\n    # Locate")
s=s.replace("'['+str(j+1)+'] '+anchor","'['+str(j+1)+']'")
s=s.replace("  c.save();ov=",'''   gloss=[('diminishing','diminishing returns 边际收益递减'),('tuning','hyperparameter tuning 超参数调优'),('epochs','epoch 训练轮次'),('FPO','FPO 浮点运算次数'),('inference','inference 推理'),('rebound','rebound effect 反弹效应'),('life-cycle','life-cycle assessment 生命周期评估'),('life cycle','life cycle 生命周期'),('intergenerational','intergenerational equity 代际公平'),('EPR','EPR 生产者责任延伸'),('NRBV','NRBV 自然资源基础观'),('consensus','consensus mechanism 共识机制'),('sourcing','ethical sourcing 负责任采购')]
   for term,translation in gloss:
    if term.lower() in note.lower():
     c.setFont('STSong-Light',8);c.drawString(w+12,ny-23-(k+1)*12,translation);break
  c.save();ov=''' )
p.write_text(s,encoding='utf-8')
