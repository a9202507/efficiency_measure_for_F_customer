from visa_function import *
import pandas as pd
import time
devices=get_visa_resource_list()

### 以下部份需依儀器及測試條件修改

daq=agilentDAQ(devices[3]) #從visa_function.py 中的agilentDAQ類別，建立資料擷取器物件
dc_source=gpibChromaDCSource(devices[1])
chroma_eload=chromaEload(devices[2]) ##建立負載機物件
my_channel_setting=[105,106,107,108] #設定擷取器要讀取channel
input_voltage=12.05 #設定DC source 的電壓值
input_current=10    #設定DC source 的電流值
load_list=[0,4,8,12] #設定負載電流條件
during_on_time=1 #設定負載機拉載的持續時間
during_off_time=2 #設定負載機無載的休息時間
save_filename='mycsv.csv' # 設定輸出檔名，限.csv
###


# 建立 real_all_daq_channel 函式，輸入channels的list物件，以及delay的參數
# channels list 內容長度不限，但限定放整數數值
def read_all_daq_channel(*channels,delay=0.5): 
    result=list()
    for channel in channels:
        
        daq.read_channel_voltage(channel) #控制daq 讀取特定channel 的電壓值
        time.sleep(delay)

        result.append(daq.get_voltage_result()) #將讀到的channel 電壓值放在result list 物件中
    return result
        


dc_source.set_voltage(input_voltage)
dc_source.set_current(input_current)
df_columns_list=['iout','input_current'] ##建立表格欄位名稱
df_columns_list.extend(my_channel_setting) ## 建立表格欄位名稱
df=pd.DataFrame(columns=df_columns_list) ##建立輸出表格物件，並設定欄位名稱 此為總輸出表格
dc_source.on()
for load in load_list:
    chroma_eload.setTotalCurrent(load) ##設定電流
    chroma_eload.total_load_on() ## 拉載
    time.sleep(during_on_time) ## set loading on time
    my_result_list=read_all_daq_channel(*my_channel_setting,delay=0.2) #一次讀取所有channel 的值
    dc_source.measure_current() ##讀取dc source 的電流值
    input_curren_value=float(dc_source.measure_current_value) ## 處理dc source 電流值
    chroma_eload.total_load_off() ## 取消拉載
    df_result_temp_list=[load,input_curren_value] #把負載值串在第一個位置
    
    df_result_temp_list.extend(my_result_list) ## 在輸出電流值之後，串上每個擷取器讀到頻道的讀值
    df_temp=pd.DataFrame([df_result_temp_list],columns=df_columns_list) ##轉成df格式
    df=df.append(df_temp,ignore_index=True) ## 將單次量測結果，串到結輸出表格裡面
    time.sleep(during_off_time) ## set loading off time
dc_source.off() #測試結束，關掉 dc_source
df.to_csv(save_filename) #存檔


