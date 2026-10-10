import { mountMotion } from '../../shared/motion.js';
mountMotion({intro(tl){tl.from('.hero-picture',{y:60,opacity:0,duration:1.25}).from('.hero-copy > *',{y:22,opacity:0,stagger:.09},.15).from('.script-word',{x:30,opacity:0},.65)},ambient(g){return [g.to('.seal',{rotation:8,duration:5,repeat:-1,yoyo:true,ease:'sine.inOut'})]}});
