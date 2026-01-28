import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="논리 회로 시뮬레이터 v6.0", layout="wide")

st.title("🚀 로직 플로우: 60FPS 성능 최적화")
st.write("그리기 엔진을 최적화하여 게이트 이동이 훨씬 부드러워졌습니다. (기존 20FPS → 60FPS)")

logic_gate_html = """
<div id="wrapper" style="width: 100%; height: 85vh; border: 2px solid #333; background-color: #f8f9fa; position: relative; overflow: hidden; border-radius: 10px;">
    <div style="position: absolute; top: 10px; left: 10px; z-index: 100; display: flex; flex-wrap: wrap; gap: 5px; background: rgba(255,255,255,0.9); padding: 12px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
        <button onclick="addGate('IN')">➕ IN</button>
        <button onclick="addGate('AND')">AND</button>
        <button onclick="addGate('OR')">OR</button>
        <button onclick="addGate('NOT')">NOT</button>
        <button onclick="addGate('XOR')">XOR</button>
        <button onclick="addGate('OUT')">🚩 OUT</button>
        <span style="border-left: 2px solid #ddd; margin: 0 10px;"></span>
        <button onclick="spawnPreset('SR_LATCH')" style="background-color: #e3f2fd;">SR 래치</button>
        <button onclick="spawnPreset('D_FLIP_FLOP')" style="background-color: #fff3e0;">D 플립플롭</button>
        <button onclick="spawnPreset('HALF_ADDER')" style="background-color: #f1f8e9;">반가산기</button>
        <button onclick="spawnPreset('FULL_ADDER')" style="background-color: #fce4ec;">전가산기</button>
        <button onclick="resetCanvas()" style="background-color: #ff4b4b; color: white;">초기화</button>
    </div>

    <div id="trash-can-ui" style="position: absolute; bottom: 20px; right: 20px; width: 100px; height: 100px; border: 3px dashed #ff4b4b; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #ff4b4b; font-weight: bold; background: rgba(255,75,75,0.1); pointer-events: none; z-index: 5;">
        TRASH
    </div>

    <canvas id="gateCanvas" style="position: absolute; top: 0; left: 0; z-index: 10; cursor: crosshair;"></canvas>
</div>

<script>
    const canvas = document.getElementById('gateCanvas');
    const ctx = canvas.getContext('2d');
    const wrapper = document.getElementById('wrapper');

    function resizeCanvas() {
        canvas.width = wrapper.clientWidth;
        canvas.height = wrapper.clientHeight;
    }
    window.onresize = resizeCanvas;
    resizeCanvas();

    const GRID_SIZE = 25;
    let gates = [];
    let connections = [];
    let draggingGate = null;
    let linkingNode = null;
    let selectionBox = null;
    let selectedGates = [];
    let mousePos = { x: 0, y: 0 };
    let mouseDownPos = { x: 0, y: 0 };

    function createGate(type, x, y) {
        return {
            id: 'g_' + Math.random().toString(36).substr(2, 9),
            type: type, x: x, y: y, r: 30,
            inputs: (['AND', 'OR', 'XOR'].includes(type)) ? [{v:0}, {v:0}] : [{v:0}],
            outputValue: 0, nextOutputValue: 0, state: 0 
        };
    }

    function addGate(type) { gates.push(createGate(type, 100, 150)); }

    function spawnPreset(name) {
        const startX = 150, startY = 300;
        if (name === 'D_FLIP_FLOP') {
            const inD = createGate('IN', startX, startY - 100);
            const inClk = createGate('IN', startX, startY + 100);
            const notIn = createGate('NOT', startX + 80, startY - 60);
            const and1 = createGate('AND', startX + 180, startY - 80);
            const and2 = createGate('AND', startX + 180, startY + 80);
            const or1 = createGate('OR', startX + 300, startY - 50);
            const not1 = createGate('NOT', startX + 380, startY - 50);
            const or2 = createGate('OR', startX + 300, startY + 50);
            const not2 = createGate('NOT', startX + 380, startY + 50);
            const outQ = createGate('OUT', startX + 480, startY - 50);
            gates.push(inD, inClk, notIn, and1, and2, or1, not1, or2, not2, outQ);
            connections.push({fromId: inD.id, toId: and1.id, toIdx: 0}, {fromId: inD.id, toId: notIn.id, toIdx: 0},
                             {fromId: notIn.id, toId: and2.id, toIdx: 1}, {fromId: inClk.id, toId: and1.id, toIdx: 1},
                             {fromId: inClk.id, toId: and2.id, toIdx: 0}, {fromId: and1.id, toId: or1.id, toIdx: 0},
                             {fromId: and2.id, toId: or2.id, toIdx: 1}, {fromId: or1.id, toId: not1.id, toIdx: 0},
                             {fromId: or2.id, toId: not2.id, toIdx: 0}, {fromId: not1.id, toId: or2.id, toIdx: 0},
                             {fromId: not2.id, toId: or1.id, toIdx: 1}, {fromId: not1.id, toId: outQ.id, toIdx: 0});
        } else if (name === 'HALF_ADDER') {
            const inA = createGate('IN', startX, startY - 60);
            const inB = createGate('IN', startX, startY + 60);
            const xor = createGate('XOR', startX + 150, startY - 40);
            const and = createGate('AND', startX + 150, startY + 40);
            const outS = createGate('OUT', startX + 300, startY - 40);
            const outC = createGate('OUT', startX + 300, startY + 40);
            gates.push(inA, inB, xor, and, outS, outC);
            connections.push({fromId: inA.id, toId: xor.id, toIdx: 0}, {fromId: inA.id, toId: and.id, toIdx: 0},
                             {fromId: inB.id, toId: xor.id, toIdx: 1}, {fromId: inB.id, toId: and.id, toIdx: 1},
                             {fromId: xor.id, toId: outS.id, toIdx: 0}, {fromId: and.id, toId: outC.id, toIdx: 0});
        } else if (name === 'FULL_ADDER') {
            const inA = createGate('IN', startX, startY - 80), inB = createGate('IN', startX, startY), inCin = createGate('IN', startX, startY + 80);
            const xor1 = createGate('XOR', startX + 120, startY - 40), xor2 = createGate('XOR', startX + 260, startY);
            const and1 = createGate('AND', startX + 260, startY + 100), and2 = createGate('AND', startX + 120, startY + 180);
            const or1 = createGate('OR', startX + 400, startY + 140), outS = createGate('OUT', startX + 420, startY), outC = createGate('OUT', startX + 520, startY + 140);
            gates.push(inA, inB, inCin, xor1, xor2, and1, and2, or1, outS, outC);
            connections.push({fromId: inA.id, toId: xor1.id, toIdx: 0}, {fromId: inB.id, toId: xor1.id, toIdx: 1}, {fromId: xor1.id, toId: xor2.id, toIdx: 0}, {fromId: inCin.id, toId: xor2.id, toIdx: 1}, {fromId: xor1.id, toId: and1.id, toIdx: 0}, {fromId: inCin.id, toId: and1.id, toIdx: 1}, {fromId: inA.id, toId: and2.id, toIdx: 0}, {fromId: inB.id, toId: and2.id, toIdx: 1}, {fromId: and1.id, toId: or1.id, toIdx: 0}, {fromId: and2.id, toId: or1.id, toIdx: 1}, {fromId: xor2.id, toId: outS.id, toIdx: 0}, {fromId: or1.id, toId: outC.id, toIdx: 0});
        } else if (name === 'SR_LATCH') {
            const inS = createGate('IN', startX, startY - 80), inR = createGate('IN', startX, startY + 80);
            const nor1 = createGate('OR', startX + 150, startY - 50), not1 = createGate('NOT', startX + 240, startY - 50);
            const nor2 = createGate('OR', startX + 150, startY + 50), not2 = createGate('NOT', startX + 240, startY + 50);
            const outQ = createGate('OUT', startX + 350, startY - 50);
            gates.push(inS, inR, nor1, not1, nor2, not2, outQ);
            connectionsoy.push({fromId: inS.id, toId: nor1.id, toIdx: 0}, {fromId: inR.id, toId: nor2.id, toIdx: 1}, {fromId: nor1.id, toId: not1.id, toIdx: 0}, {fromId: nor2.id, toId: not2.id, toIdx: 0}, {fromId: not1.id, toId: nor2.id, toIdx: 0}, {fromId: not2.id, toId: nor1.id, toIdx: 1}, {fromId: not1.id, toId: outQ.id, toIdx: 0});
        }
    }

    // 1. 로직 엔진 (50ms 마다 독립 실행)
    setInterval(() => {
        gates.forEach(g => {
            g.inputs.forEach(ins => ins.v = 0);
            connections.forEach(conn => {
                if (conn.toId === g.id) {
                    const src = gates.find(s => s.id === conn.fromId);
                    if (src) g.inputs[conn.toIdx].v = src.outputValue;
                }
            });
        });
        gates.forEach(g => {
            if (g.type === 'IN') g.nextOutputValue = g.state;
            else if (g.type === 'AND') g.nextOutputValue = (g.inputs[0].v && g.inputs[1].v) ? 1 : 0;
            else if (g.type === 'OR') g.nextOutputValue = (g.inputs[0].v || g.inputs[1].v) ? 1 : 0;
            else if (g.type === 'NOT') g.nextOutputValue = g.inputs[0].v ? 0 : 1;
            else if (g.type === 'XOR') g.nextOutputValue = (g.inputs[0].v ^ g.inputs[1].v) ? 1 : 0;
            else if (g.type === 'OUT') g.nextOutputValue = g.inputs[0].v;
        });
        gates.forEach(g => { g.outputValue = g.nextOutputValue; });
    }, 50);

    // 2. 렌더링 엔진 (브라우저 주사율에 맞춰 60FPS 실행)
    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // 격자
        ctx.strokeStyle = '#e9ecef'; ctx.lineWidth = 1;
        for(let i=0; i<canvas.width; i+=GRID_SIZE){ ctx.beginPath(); ctx.moveTo(i,0); ctx.lineTo(i,canvas.height); ctx.stroke(); }
        for(let j=0; j<canvas.height; j+=GRID_SIZE){ ctx.beginPath(); ctx.moveTo(0,j); ctx.lineTo(canvas.width,j); ctx.stroke(); }

        if (selectionBox) {
            ctx.fillStyle = 'rgba(255, 235, 59, 0.2)'; ctx.strokeStyle = '#fbc02d'; ctx.lineWidth = 1;
            ctx.fillRect(selectionBox.x, selectionBox.y, selectionBox.w, selectionBox.h);
            ctx.strokeRect(selectionBox.x, selectionBox.y, selectionBox.w, selectionBox.h);
        }

        connections.forEach(conn => {
            const src = gates.find(g => g.id === conn.fromId);
            const dest = gates.find(g => g.id === conn.toId);
            if(src && dest) {
                const sX = src.x + src.r, sY = src.y;
                const eX = dest.x - dest.r, eY = dest.y + (dest.inputs.length > 1 ? (conn.toIdx === 0 ? -15 : 15) : 0);
                ctx.beginPath(); ctx.strokeStyle = src.outputValue ? '#FFD700' : '#adb5bd'; ctx.lineWidth = 4;
                const dist = Math.abs(eX - sX);
                ctx.moveTo(sX, sY);
                ctx.bezierCurveTo(sX + dist/1.5 + 20, sY, eX - dist/1.5 - 20, eY, eX, eY);
                ctx.stroke();
            }
        });

        gates.forEach(g => {
            const isSelected = selectedGates.includes(g);
            ctx.beginPath(); ctx.arc(g.x, g.y, g.r, 0, Math.PI*2);
            ctx.fillStyle = (g.type === 'OUT' && g.outputValue) ? '#fff176' : (g.type === 'IN' && g.state) ? '#64b5f6' : '#ffffff';
            ctx.fill(); ctx.strokeStyle = isSelected ? '#fbc02d' : '#495057'; ctx.lineWidth = isSelected ? 4 : 2; ctx.stroke();
            ctx.fillStyle = '#212529'; ctx.font = 'bold 13px Arial'; ctx.textAlign = 'center';
            ctx.fillText(g.type === 'IN' ? g.state : g.type, g.x, g.y + 5);
            g.inputs.forEach((_, i) => {
                ctx.beginPath(); ctx.arc(g.x - g.r, g.y + (g.inputs.length > 1 ? (i === 0 ? -15 : 15) : 0), 6, 0, Math.PI*2);
                ctx.fillStyle = '#ff6b6b'; ctx.fill();
            });
            if(g.type !== 'OUT') {
                ctx.beginPath(); ctx.arc(g.x + g.r, g.y, 6, 0, Math.PI*2);
                ctx.fillStyle = '#51cf66'; ctx.fill();
            }
        });

        if (linkingNode) {
            ctx.beginPath(); ctx.setLineDash([5,5]); ctx.moveTo(linkingNode.x, linkingNode.y);
            ctx.lineTo(mousePos.x, mousePos.y); ctx.stroke(); ctx.setLineDash([]);
        }
        
        requestAnimationFrame(draw); // 다음 프레임 예약
    }
    requestAnimationFrame(draw); // 애니메이션 시작

    canvas.onmousedown = (e) => {
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left, y = e.clientY - rect.top;
        mouseDownPos = {x, y};
        for (let g of gates) {
            for (let i = 0; i < g.inputs.length; i++) {
                const pX = g.x - g.r, pY = g.y + (g.inputs.length > 1 ? (i === 0 ? -15 : 15) : 0);
                if (Math.hypot(pX - x, pY - y) < 12) { connections = connections.filter(c => !(c.toId === g.id && c.toIdx === i)); return; }
            }
            if (g.type !== 'OUT' && Math.hypot(g.x + g.r - x, g.y - y) < 12) { linkingNode = { fromId: g.id, x: g.x + g.r, y: g.y }; return; }
        }
        let clickedGate = gates.find(g => Math.hypot(g.x - x, g.y - y) < g.r);
        if (clickedGate) {
            if (!selectedGates.includes(clickedGate)) selectedGates = [clickedGate];
            draggingGate = clickedGate;
            selectedGates.forEach(g => { g.offsetX = x - g.x; g.offsetY = y - g.y; });
            return;
        }
        selectedGates = []; selectionBox = { x: x, y: y, w: 0, h: 0 };
    };

    canvas.onmousemove = (e) => {
        const rect = canvas.getBoundingClientRect();
        mousePos = { x: e.clientX - rect.left, y: e.clientY - rect.top };
        if (draggingGate) {
            selectedGates.forEach(g => { g.x = mousePos.x - g.offsetX; g.y = mousePos.y - g.offsetY; });
        } else if (selectionBox) {
            selectionBox.w = mousePos.x - selectionBox.x; selectionBox.h = mousePos.y - selectionBox.y;
            const x1 = Math.min(selectionBox.x, mousePos.x), x2 = Math.max(selectionBox.x, mousePos.x);
            const y1 = Math.min(selectionBox.y, mousePos.y), y2 = Math.max(selectionBox.y, mousePos.y);
            selectedGates = gates.filter(g => g.x > x1 && g.x < x2 && g.y > y1 && g.y < y2);
        }
    };

    canvas.onmouseup = (e) => {
        if (draggingGate) {
            if (mousePos.x > canvas.width - 120 && mousePos.y > canvas.height - 120) {
                const ids = selectedGates.map(g => g.id);
                connections = connections.filter(c => !ids.includes(c.fromId) && !ids.includes(c.toId));
                gates = gates.filter(g => !ids.includes(g.id));
                selectedGates = [];
            } else if (Math.hypot(mousePos.x - mouseDownPos.x, mousePos.y - mouseDownPos.y) < 5 && draggingGate.type === 'IN') {
                draggingGate.state = draggingGate.state ? 0 : 1;
            }
        }
        if (linkingNode) {
            gates.forEach(g => {
                g.inputs.forEach((_, idx) => {
                    const pX = g.x - g.r, pY = g.y + (g.inputs.length > 1 ? (idx === 0 ? -15 : 15) : 0);
                    if (Math.hypot(pX - mousePos.x, pY - mousePos.y) < 18) connections.push({ fromId: linkingNode.fromId, toId: g.id, toIdx: idx });
                });
            });
        }
        draggingGate = null; linkingNode = null; selectionBox = null;
    };

    function resetCanvas() { gates = []; connections = []; selectedGates = []; }
</script>
"""

components.html(logic_gate_html, height=900)