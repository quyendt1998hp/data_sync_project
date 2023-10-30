# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi
# import pymongo
​
# # Replace the placeholder with your Atlas connection string
# uri = "mongodb://localhost:27017"
# # Set the Stable API version when creating a new client
# client = MongoClient(uri, server_api=ServerApi('1'))
                          
# # Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)
​
import pprint
import pymongo
from tabulate import tabulate
client = pymongo.MongoClient("mongodb://localhost:27017/")
​
db = client["sinhviendb4"]
​
collection = db["sinhvien"]
​
​
​
def main_menu():
    while True:
        print("\nMain Menu:")
        print("1. Thêm sinh viên")
        print("2. Hiển thị sinh viên và điểm số")
        print("3. Xóa sinh viên theo id nhập vào từ bàn phím")
        print("4. Tìm kiếm sinh viên theo tên, tuổi")
        print("5. Tìm kiếm sinh viên có điểm môn xxx > yyy")
        print("6. Tìm kiến sinh viên có tổng điểm 3 môn > zzz")
        print("7. Thoát ")
        choice = input("Enter your choice: ")
​
​
        if choice == '1':
            option1()
        elif choice == '2':
            option2()
        elif choice == '3':
            option3()
        elif choice == '4':
            option4()
        elif choice == '5':
            option5()
        elif choice == '6':
            option6()
        elif choice == '7':
            break
        else:
            print("Invalid choice. Please select a valid option.")
​
#Thêm sinh viên
def option1():
    print("|| Nhập mã số(id) sinh viên:")
    id = input()
    print("|| Nhập tên sinh viên:")
    ten = input()
    print("|| Nhập tuổi:")
    tuoi = input()
    print("|| Nhập giới tính:")
    gioitinh = input()
    print("|| Điểm toán:")
    toan = input()
    print("|| Điểm lý:")
    ly = input()
    print("|| Điểm hóa:")
    hoa = input()
​
    sv_data = {
        "id":id,
        "name": ten,
        "age": tuoi,
        "gender": gioitinh,
        "scores": [
            {"Math":toan},
            {"Physics": ly},
            {"Chemistry": hoa}
        ]
    }
​
    try:
        collection.insert_one(sv_data)
        print("thêm sinh viên thành công")
        input("Press Enter to continue...")
    except:
        print("Xảy ra lỗi khi lưu sinh viên")
        input("Press Enter to continue...")
​
#Hiển thị sinh viên
def option2():
    all_students = collection.find()
​
    # Chuyển dữ liệu thành một danh sách để sử dụng tabulate
    table_data = []
    for student in all_students:
        table_data.append([
            student["id"],
            student["name"],
            student["age"],
            student["gender"],
            student["scores"][0]["Math"],
            student["scores"][1]["Physics"],
            student["scores"][2]["Chemistry"]
        ])
​
    # Danh sách các tiêu đề cột
    headers = ["id","Tên", "Tuổi", "Giới tính", "Điểm Toán", "Điểm Lý", "Điểm Hóa"]
​
    # In ra bảng
    table = tabulate(table_data, headers, tablefmt="grid")
    print(table)
    input("Press Enter to continue...")
​
#Xóa sinh viên
def option3():
    print("|| Nhập id sinh viên cần xóa:")
    id_sv = input()
​
    try:
        collection.remove( { "id": id_sv } )
        print("Xóa sinh viên thành công")
    except:
        print("không tìm thấy sinh viên")
    input("Press Enter to continue...")
​
#Tìm kiếm sinh viên theo tên, tuổi
def option4():
    print("Tìm kiếm sinh viên theo tên, tuổi")
    print("|| Nhập tên:")
    ten = input()
    print("|| Nhập tuổi:")
    tuoi = input()
    sv = collection.find_one({"name": ten,"age": tuoi})
    print(sv)
    input("Press Enter to continue...")
​
#Tìm kiếm sinh viên theo môn và điểm số xxx > yyy"
def option5():
    print("Tìm kiếm sinh viên theo điểm số:")
    print("|| Nhập tên môn học:")
    subject = input()
    print("|| Nhập mốc điểm số:")
    score = input()
    print("Những sinh viên tìm được:")
    if subject == "Toán":
​
        #     sv_data = {
        #           "id":id,
        #           "name": ten,
        #           "age": tuoi,
        #           "gender": gioitinh,
        #           "scores": [
        #                   {"Math":toan},
        #                   {"Physics": ly},
        #                   {"Chemistry", hoa}
        #                   ]
        #       }
        
        sv = collection.find({"scores": {"$elemMatch": {"Math": {"$gt": score }}}})
    
        for s in sv:
            print(s)
    input("Press Enter to continue...")
​
#Tìm kiếm sinh viên theo tổng điểm 3 môn
def option6():
    print("Tìm kiếm sinh viên theo tổng điểm:")
    print("|| Nhập mốc điểm:")
    point = input()
​
    all_students = collection.find()
    sv_cantim = []
    # Chuyển dữ liệu thành một danh sách để sử dụng tabulate
    table_data = []
    for student in all_students:
        tongdiem = int(student["scores"][0]["Math"]) + int(student["scores"][1]["Physics"]) + int(student["scores"][2]["Chemistry"])
        print(tongdiem)
        if tongdiem > int(point):
            sv_cantim.append(student)
    print("Các sinh viên có tổng diểm 3 môn lớn hơn "+point+" là:")
    print(sv_cantim)
    
​
if __name__ == "__main__":
    main_menu()
