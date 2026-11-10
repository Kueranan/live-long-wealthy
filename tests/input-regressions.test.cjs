const {test}=require('node:test');
const assert=require('node:assert/strict');
const {readFileSync}=require('node:fs');
const vm=require('node:vm');
const html=readFileSync(require('node:path').join(__dirname,'../web/index.html'),'utf8');
const inputCode=html.slice(html.indexOf('const LIM='),html.indexOf('function setFill('));
const context=vm.createContext({document:{},baht:String});
vm.runInContext(inputCode,context);
const parse=(key,text)=>vm.runInContext(`parseTyped(${JSON.stringify(key)},${JSON.stringify(text)})`,context);
test('decimal interest and formatted amounts retain their values',()=>{
 assert.equal(parse('drate','2.5').value,2.5);
 assert.equal(parse('income','20,000.50').value,20000.5);
});
test('negative, malformed, empty and fractional age inputs are rejected',()=>{
 for(const [key,text] of [['debt','-10000'],['drate','-2.5'],['income','12,34'],['income','abc100'],['income',''],['age','23.5']]) assert.ok(parse(key,text).error,`${key}: ${text}`);
});
test('positive values retain supported limits',()=>{
 assert.equal(parse('retage','78').value,75);
 assert.equal(parse('income','300000').value,300000);
});
const whatIfCode=html.slice(html.indexOf('  const W=['),html.indexOf('  const deltas=W.map'));
const choices=retage=>{const c=vm.createContext({p:{retage,saving:1500,spend:15000,risk:'1',debt:0,smart:false},baht:String});vm.runInContext(inputCode+'\n'+whatIfCode+'\nglobalThis.result=W;',c);return c.result;};
test('delaying retirement adds exactly three years within the supported limit',()=>{
 for(const age of [60,70,72]){const w=choices(age).find(w=>w.t==='เกษียณช้าลง 3 ปี');assert.equal(w.ch.retage,age+3);assert.equal(w.d,`อายุ ${age+3} ปี`);}
});
test('retirement option is absent when three more years exceed the limit',()=>{
 for(const age of [73,74,75]) assert.equal(choices(age).some(w=>w.t==='เกษียณช้าลง 3 ปี'),false);
});
