from func import set_temperature, set_output, generate_defect_data, get_defect_data, run_simulation, initial, load_material

# 初始化
initial()
load_material()

# 设定温度及输出模式
set_temperature(800)
#set_output('distribution', 'time uniform', 1)
set_output('count', 'time log', 100)

# 导入初始缺陷分布
generate_defect_data(5000)
#get_defect_data('PKA.txt')

# 运行模拟
run_simulation(50)