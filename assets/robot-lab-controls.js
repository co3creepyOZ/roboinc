'use strict';
document.querySelectorAll('[data-decision-game]').forEach(root=>{
 const stage=root.querySelector('.rv-stage'),route=root.querySelector('.dg-route');
 if(!stage||!route||stage.dataset.editable)return;
 stage.dataset.editable='true';
 const path=stage.querySelector('.rv-path');
 route.querySelectorAll('[data-step]').forEach(step=>{
  const index=Number(step.dataset.step);
  let node=path.querySelector('[data-node="'+index+'"]');
  if(!node){node=document.createElement('div');node.className='rv-node rv-else';node.dataset.node=index;path.insertBefore(node,path.querySelector('.rv-finish'));}
  const controls=document.createElement('div');controls.className='rv-edit-controls';
  const buddy=document.createElement('span');buddy.className='rv-buddy';buddy.textContent='🤖';buddy.setAttribute('aria-hidden','true');
  // Move the actual controls, retaining IDs, values and existing event listeners.
  while(step.firstChild)controls.append(step.firstChild);
  node.prepend(buddy);
  const oldLabel=[...node.children].filter(el=>el!==buddy&&el.tagName!=='SMALL');
  oldLabel.forEach(el=>el.remove());
  node.prepend(controls);node.prepend(buddy);
  node.dataset.step=step.dataset.step;
  if(!node.querySelector('small')){const status=document.createElement('small');status.textContent='Якщо жодна умова не спрацювала';node.append(status);}
 });
 const current=route.querySelector('[data-current]');if(current)stage.append(current);
 route.remove();
 const actions=root.querySelector('.rg-actions');if(actions)stage.append(actions);
 const status=root.querySelector('[data-status]');if(status)stage.append(status);
 const log=root.querySelector('[data-log]');
 if(log){const details=document.createElement('details');details.className='rv-test-results';const summary=document.createElement('summary');summary.textContent='Результати перевірок';details.append(summary,log);stage.append(details);}
 const run=stage.querySelector('[data-run]');if(run)run.textContent='▶ Перевірити всі нахили / тести';
});
