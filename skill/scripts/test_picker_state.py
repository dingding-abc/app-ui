"""Optional Node check of shared picker state, without browser/DOM rendering."""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from hour_picker import SCRIPT, STATE_SCRIPT

CASES = r"""
const assert = require('node:assert/strict');
const hours = Array.from({length:24}, (_,i) => i);
const minutes = Array.from({length:60}, (_,i) => i);
let count = 0;
function test(name, run) {run(); count++; console.log('PASS: ' + name);}
test('both columns must settle before committing', () => {
  const s = createWheelState([hours,minutes],[9,30]);
  s.begin(0); s.begin(1); s.move(0,14); s.move(1,45); s.settle(0);
  assert.equal(s.commit(),false); assert.deepEqual(s.saved(),[9,30]);
  s.settle(1); assert.equal(s.commit(),true); assert.deepEqual(s.saved(),[14,45]);
});
test('cancel restores full last confirmed pair while moving', () => {
  const s = createWheelState([hours,minutes],[9,30]);
  s.move(0,14); s.move(1,45); s.commit();
  s.begin(0); s.begin(1); s.move(0,0); s.move(1,0); s.cancel();
  assert.deepEqual(s.values(),[14,45]); assert.equal(s.ready(),true);
});
test('minute boundaries do not carry into hours', () => {
  const s = createWheelState([hours,minutes],[23,59]);
  s.move(1,60); assert.deepEqual(s.values(),[23,0]);
  s.move(1,-1); assert.deepEqual(s.values(),[23,59]);
  s.move(0,24); assert.deepEqual(s.values(),[0,59]);
});
test('hour zero can move directly to 23 and back to zero', () => {
  const s = createWheelState([hours],[0]);
  s.move(0,s.index(0)-1); assert.deepEqual(s.values(),[23]);
  s.move(0,s.index(0)+1); assert.deepEqual(s.values(),[0]);
});
test('all minute steps wrap to the last valid minute in either direction', () => {
  for (const step of [1,5,10,15,30]) {
    const candidates = minutes.filter(n => n % step === 0);
    const s = createWheelState([hours,candidates],[9,0]);
    s.move(1,-1); assert.deepEqual(s.values(),[9,60-step]);
    s.move(1,s.index(1)+1); assert.deepEqual(s.values(),[9,0]);
  }
});
test('recentring retains the selected value and fractional row offset', () => {
  for (const count of [2,4,12,24,60]) {
    for (const position of [-0.2,0,0.3,count-0.2,5*count+0.7,7*count-1]) {
      const centered = recenterWheelPosition(position,count);
      assert.ok(centered >= 3*count && centered < 4*count);
      assert.equal(wrapWheelIndex(centered,count),wrapWheelIndex(position,count));
      assert.ok(Math.abs((centered-position)/count-Math.round((centered-position)/count)) < 1e-10);
    }
  }
});
test('many revolutions and cancelling across midnight preserve confirmed values', () => {
  const s = createWheelState([hours,minutes],[23,59]);
  s.move(0,24*100); s.move(1,60*100); s.commit();
  assert.deepEqual(s.saved(),[0,0]);
  s.move(0,-24*100-1); s.move(1,-60*100-1);
  assert.deepEqual(s.values(),[23,59]);
  s.cancel(); assert.deepEqual(s.values(),[0,0]);
});
test('five-minute row indices resolve to actual minute values', () => {
  const s = createWheelState([hours,minutes.filter(n => n % 5 === 0)],[9,30]);
  assert.equal(s.index(1),6); s.move(1,11); s.commit();
  assert.deepEqual(s.saved(),[9,55]);
});
test('nearest row selection and independent columns', () => {
  const s = createWheelState([hours,minutes],[9,30]);
  s.move(1,42.6); assert.deepEqual(s.values(),[9,43]);
  s.move(0,10.2); assert.deepEqual(s.values(),[10,43]);
});
test('hour-only cancellation remains compatible', () => {
  const s = createWheelState([hours],[9]);
  s.move(0,23); s.cancel(); assert.deepEqual(s.values(),[9]);
  s.move(0,14); s.commit(); assert.deepEqual(s.saved(),[14]);
});
test('invalid initial step rejected without rounding', () => {
  assert.throws(() => createWheelState([hours,[0,15,30,45]],[9,32]),RangeError);
});
console.log(count + ' state scenarios passed; browser interaction not tested.');
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node',default=shutil.which('node'))
    args = parser.parse_args()
    if not args.node:
        parser.error('Node required for optional state check; use --node with its path')
    subprocess.run([args.node,'--check'],input=SCRIPT,text=True,check=True)
    subprocess.run([args.node],input=STATE_SCRIPT+CASES,text=True,check=True)
