import mdfreader

# MDF4 파일 읽기
mdf = mdfreader.Mdf('Test/00000001-642C1E5E.MF4')

# 모든 채널 확인
print(mdf.keys())

# 특정 CAN 채널 데이터 가져오기
can_data = mdf.get_channel_data('CAN_Channel_1')
print(can_data.head())