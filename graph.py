import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import json
import pandas as pd

plt.rcParams['font.family'] = 'SimHei'
plt.rcParams['font.size'] = 18

def m_graph(fpos, f, bpos, b, l, n=5000):
    forces = list(map(lambda x: (x[0], x[1] / 1000), sorted(zip(fpos, f), key=lambda x: x[0])))
    bends = list(map(lambda x: (x[0], x[1] / 1000), sorted(zip(bpos, b), key=lambda x: x[0])))
    pos_values = np.linspace(0, l, n)
    M_values = np.zeros(n)
    
    critical_points = dict()
    for i in range(len(forces) - 1):
        fpos, f = forces[i]
        mask = pos_values > fpos
        critical_points[fpos] = M_values[mask][0]
        new_val = (pos_values - fpos) * f
        M_values[mask] += new_val[mask]
        
    if 0 in critical_points:
        del critical_points[0]
        
    for bend in bends:
        mask = pos_values >= bend[0]
        M_values[mask] += bend[1]
        for k in critical_points.keys():
            if k > bend[0]:
                critical_points[k] += bend[1]
            elif k == bend[0]:
                # 保留最大值
                if critical_points[k] * bend[1] > 0:
                    critical_points[k] += bend[1]
        
    fig = plt.figure(figsize=(12, 3))
    plt.xlabel('位置 [mm]')
    plt.ylabel('转矩 [Nm]')
    plt.plot(pos_values, M_values)
    plt.xlim(0, l)
    plt.ylim(min(M_values), max(M_values))
    for x, y in critical_points.items():
        plt.text(x, y, f'{y: .4e}', fontsize=14, color='red')
    plt.grid()
    plt.tight_layout()
    return fig
    

st.markdown('# 简易弯矩图绘图')

# 初始化数据容器
if 'forces' not in st.session_state:
    st.session_state.forces = []
    st.session_state.moments = []

# 力输入模块
def add_force():
    pos = float(st.session_state.force_pos_input)
    direction = st.session_state.force_dir_select
    mag = float(st.session_state.force_mag_input)
    st.session_state.forces.append({
        'position': pos,
        'direction': direction,
        'magnitude': mag
    })

def delete_force(index):
    del st.session_state.forces[index]

# 弯矩输入模块
def add_moment():
    pos = float(st.session_state.moment_pos_input)
    direction = st.session_state.moment_dir_select
    mag = float(st.session_state.moment_mag_input)
    st.session_state.moments.append({
        'position': pos,
        'direction': direction,
        'magnitude': mag
    })

def delete_moment(index):
    del st.session_state.moments[index]

# 主界面布局
st.title("横梁杆荷载输入系统")

# 力输入部分
with st.container():
    st.subheader("轴力/剪力输入")
    st.markdown("#### 输入参数：位置(m)、方向、大小(kN)")
    
    # 添加新力输入
    with st.form(key='force_form'):
        st.number_input("位置", key='force_pos_input')
        st.selectbox("方向", ['上', '下'], key='force_dir_select')
        st.number_input("大小", key='force_mag_input')
        st.form_submit_button('添加力', on_click=add_force)
    
    # 显示现有力数据
    st.table(pd.DataFrame(
        [[f['position'], f['direction'], f['magnitude']] for f in st.session_state.forces],
        columns=["位置", "方向", '大小']
    ))

    # 删除功能
    if st.session_state.forces:
        for i, _ in enumerate(st.session_state.forces):
            st.button(f"删除力 {i}", on_click=lambda idx=i: delete_force(idx))

# 弯矩输入部分
with st.container():
    st.subheader("弯矩输入")
    st.markdown("#### 输入参数：位置(m)、方向、大小(kNm)")
    
    # 添加新弯矩输入
    with st.form(key='moment_form'):
        st.number_input("位置", key='moment_pos_input')
        st.selectbox("方向", ['顺时针', '逆时针'], key='moment_dir_select')
        st.number_input("大小", key='moment_mag_input')
        st.form_submit_button("添加弯矩", on_click=add_moment)
    
    # 显示现有弯矩数据
    st.table(pd.DataFrame(
        [[m['position'], m['direction'], m['magnitude']] for m in st.session_state.moments],
        columns=["位置", "方向", '大小']
    ))

    # 删除功能
    if st.session_state.moments:
        for i, _ in enumerate(st.session_state.moments):
            st.button(f"删除弯矩 {i}", on_click=lambda idx=i: delete_moment(idx))

if st.button("开始作图"):
    force_pos = [f['position'] for f in st.session_state.forces]
    forces = [f['magnitude'] if f['direction'] == '下' else -f['magnitude'] for f in st.session_state.forces] # 向下的力为正
    bend_pos = [f['position'] for f in st.session_state.moments]
    bends = [f['magnitude'] if f['direction'] == '逆时针' else -f['magnitude'] for f in st.session_state.moments] # 逆时针为正
    tors_pos = []
    axle_length = 128+89
    st.pyplot(m_graph(force_pos, forces, bend_pos, bends, axle_length))
