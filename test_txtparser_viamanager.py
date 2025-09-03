
from Module.manager.parser_manager import get_parser
import Module.utils.dataframe as candata
def test_txt_via_manager():
    # 1. Parser 얻기 (파일 경로, 타입)
    path = "Sample/Hyundai i20/Hyundai_i20_01_03_2021_CANcaseXL_Static.txt"
    parser = get_parser(path)
    
    # 2. 파일 파싱
    messages = parser.parse()
    
    # 3. 상위 3개 메시지만 출력
    #for msg in messages[:3]:
    #    print("CANMessage:")
    #    print(f"  type     : {msg.type}")
    #    print(f"  timestamp: {msg.timestamp}")
    #    print(f"  can_id   : {msg.can_id}")
    #    print(f"  dlc      : {msg.dlc}")
    #    print(f"  data     : {msg.data}")
    #    print(f"  channel  : {msg.channel}")
    #    print("-----")
    
    return messages

if __name__ == "__main__":
    messages = test_txt_via_manager()
    df = candata.messages_to_dataframe(messages)

