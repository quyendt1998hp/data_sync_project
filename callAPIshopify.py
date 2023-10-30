import pprint
import requests
import json
import time
base_url = "https://what-a-mugs.myshopify.com"
access_token = "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"
headers = {
    "X-Shopify-Access-Token": "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",
    "Content-Type": "application/json"
}
​
​
# b, CREATE
# I. Collection: 1 Smart collection, 1 Custom collection.
# Tạo smart collection
# POST /admin/api/unstable/smart_collections.json
endpoint = base_url + "/admin/api/unstable/smart_collections.json"
collection_data = {
    "smart_collection":{
        "title":"Bộ sưu tập thông minh",
        "rules":[{"column":"variant_inventory","relation":"greater_than","condition":49}]
        }
    }
response = requests.post(endpoint, headers = headers, data=json.dumps(collection_data))
smart_collection_id = json.loads(response.text).get('smart_collection').get('id')
print(response.status_code)
print(f"smart collection id la: {smart_collection_id}")
​
# Tạo custom collection
# POST /admin/api/unstable/custom_collections.json
endpoint = base_url + "/admin/api/2023-10/custom_collections.json"
collection_data = {
    "custom_collection":{
        "title":"Bộ sưu tập tùy biến"
        }
    }
response = requests.post(endpoint, headers = headers, data=json.dumps(collection_data))
custom_collection_id = json.loads(response.text).get('custom_collection').get('id')
print(response.status_code)
print(f"custom colection is la: {custom_collection_id}")
​
# # II. Product: 1 Simple product, 1 Configurable product
# # Tạo simple product
# # POST /admin/api/unstable/products.json
endpoint = base_url + "/admin/api/unstable/products.json"
product_data = {
    "product":{
        "title":"Cốc thủy tinh",
        "body_html":"<strong>Phao cứu sinh màu da cam</strong>"
        }
    }
response = requests.post(endpoint, headers = headers, data=json.dumps(product_data))
variantID_1 = json.loads(response.text).get('product').get('variants')[0].get('id')
simple_product_id = json.loads(response.text).get('product').get('id')
​
print(response.status_code)
print(f"product id: {simple_product_id}")
​
​
# update qty of product
# lấy thông tin inventory_item_id biến thể 
endpoint = base_url + f"/admin/api/2023-10/variants/{variantID_1}.json"
​
response = requests.get(endpoint, headers = headers)
inventory_item_id = json.loads(response.text).get('variant').get('inventory_item_id')
# lấy thông tin inventory_level từ location
endpoint = base_url + "/admin/api/2023-10/locations.json"
response = requests.get(endpoint, headers = headers)
locations = json.loads(response.text).get('locations')
​
location_ids = []
for location in locations:
    location_ids.append(location.get('id'))
​
​
locationstr = ",".join(map(str, location_ids))
​
endpoint = f"https://what-a-mugs.myshopify.com/admin/api/2023-10/inventory_levels.json?location_ids={locationstr}"  
response = requests.get(endpoint, headers = headers)
inventory_levels = json.loads(response.text).get('inventory_levels')
​
found_item = None
​
# Iterate through the list of dictionaries
for item in inventory_levels:
    if item.get("inventory_item_id") == inventory_item_id:
        found_item = item
        break
​
# Check if the item was found
if found_item:
    print("Item found:")
    print(found_item)
else:
    print("Item not found")
​
location_id_of_item = found_item.get('location_id')
​
​
endpoint = "https://what-a-mugs.myshopify.com/admin/api/2023-10/inventory_levels/adjust.json"
intentory_level_data = {"location_id":location_id_of_item,"inventory_item_id":inventory_item_id,"available_adjustment":99}
response = requests.post(endpoint, headers = headers, data=json.dumps(intentory_level_data))
​
# Tạo configurable product
# POST /admin/api/unstable/products.json
endpoint = base_url + "/admin/api/unstable/products.json"
product_data = {
    "product":{
        "title":"Cốc sứ",
        "body_html":"<strong>Cốc sứ có nắp đậy</strong>",
        "variants":[{"option1":"Vàng","option2":"S","price":"10.00","sku":"123"},{"option1":"Đen","option2":"S","price":"10.00","sku":"123"}],
        "options":[{"name":"Color","values":["Blue","Black"]},{"name":"Size","values":["S"]}]
        }
    }
response = requests.post(endpoint, headers = headers, data=json.dumps(product_data))
variantID_2_1 = json.loads(response.text).get('product').get('variants')[0].get('id')
variantID_2_2 = json.loads(response.text).get('product').get('variants')[1].get('id')
configurable_product_id = json.loads(response.text).get('product').get('id')
print(response.status_code)
print(f"product id: {configurable_product_id}")
​
# III. Customer: 1 customer
# Tạo customer
# POST /admin/api/unstable/customers.json
endpoint = base_url + "/admin/api/unstable/customers.json"
customer_data = {
    "customer":{
        "first_name":"Tâm",
        "last_name":"Nguyễn",
        "email":"quyen2774900@gmail.com",
        "phone":"0366596999",
        "verified_email":True,
        "addresses":[{"address1":"Tây Mỗ","city":"Hà Nội","province":"HN","phone":"0366596999","zip":"10000","last_name":"Đỗ","first_name":"Quyền","country":"VN"}],
        "password":"admin123",
        "password_confirmation":"admin123",
        "send_email_welcome":False}
}
response = requests.post(endpoint, headers = headers, data=json.dumps(customer_data))
customer_id = json.loads(response.text).get('customer').get('id')
print(response.status_code)
print(f"customer id: {customer_id}")
​
# VI. Order: 1 Order 
# Order với người dùng và sản phẩm vừa tạo
# POST /admin/api/unstable/orders.json
endpoint = base_url + "/admin/api/unstable/orders.json"
order_data = {
    "order":{
        "customer_id": customer_id,
        "line_items":[{"variant_id":variantID_1,"quantity":1},{"variant_id":variantID_2_1,"quantity":1}],
        "transactions":[{"kind":"sale","status":"success","amount":31.8}],
        "total_tax":1.8,
        "currency":"VND",
        "email":"quyen277490@gmail.com",
        "billing_address": {"first_name":"Tâm","last_name":"Nguyễn","address1":"Tây Mỗ","phone":"0366596999","city":"Hà Nội","province":"HN","country":"VN","zip":"100000"},
        "shipping_address": {"first_name":"Tâm","last_name":"Nguyễn","address1":"Tây Mỗ","phone":"0366596999","city":"Hà Nội","province":"HN","country":"VN","zip":"100000"}
        }
    }
​
response = requests.post(endpoint, headers = headers, data=json.dumps(order_data))
order_id = json.loads(response.text).get('order').get('id')
print(response.status_code)
print(f"order id la: {order_id}")
# c, UPDATE
# Update price, image, quantity for created products
# update simple product:
​
# create a new main image for product
# POST /admin/api/unstable/products/{product_id}}/images.json
endpoint = base_url + f"/admin/api/unstable/products/{simple_product_id}/images.json"
img_data_1 = {"image":{"src":"https://giadungxuanhung.com/wp-content/uploads/2023/10/IMG_0131-scaled.jpg"}}
response = requests.post(endpoint, headers = headers, data=json.dumps(img_data_1))
img_id_1 = json.loads(response.text).get('image').get('id')
img_position_1 = json.loads(response.text).get('image').get('position')
​
img_data_2 = {"image":{"src":"https://giadungxuanhung.com/wp-content/uploads/2023/10/IMG_0079-scaled.jpg"}}
endpoint = base_url + f"/admin/api/unstable/products/{configurable_product_id}/images.json"
response = requests.post(endpoint, headers = headers, data=json.dumps(img_data_2))
img_id_1 = json.loads(response.text).get('image').get('id')
print(response.status_code)
# update current image of product
# PUT /admin/api/unstable/products/{product_id}.json
# endpoint = base_url + f"/admin/api/unstable/products/{simple_product_id}.json"
# image_data_1_2 = {"image":{"src":"https://giadungxuanhung.com/wp-content/uploads/2023/10/IMG_0129-scaled.jpg"}}
# requests.put(endpoint, headers = headers, data=json.dumps(image_data_1_2))  
​
# create image for variants 
# /admin/api/unstable/products/632910392/images.json
# "variant_ids":[variantID_2_1]
# "variant_ids":[variantID_2_2]
endpoint = base_url + f"/admin/api/unstable/products/{configurable_product_id}/images.json"
image_variant_1 = {"image":{"variant_ids":[variantID_2_1],"src":"https://giadungxuanhung.com/wp-content/uploads/2023/10/IMG_0083-scaled.jpg"}}
requests.put(endpoint, headers = headers, data=json.dumps(image_variant_1))  
image_variant_2 = {"image":{"variant_ids":[variantID_2_2],"src":"https://giadungxuanhung.com/wp-content/uploads/2023/10/IMG_0081-scaled.jpg"}}
requests.put(endpoint, headers = headers, data=json.dumps(image_variant_2))  
print(response.status_code)
​
​
​
## Delete
def deleteAllCreatedData():
     #delete order /admin/api/unstable/orders/{order_id}.json
    requests.delete(base_url+f"/admin/api/unstable/orders/{order_id}.json")
​
    #delete custom collection 
    #/admin/api/unstable/custom_collections/841564295.json
    requests.delete(base_url+f"/admin/api/unstable/custom_collections/{custom_collection_id}.json")
​
    #delete smart collection
    #/admin/api/unstable/smart_collections/841564295.json
    requests.delete(base_url+f"/admin/api/unstable/custom_collections/{smart_collection_id}.json")
​
    #delete products
    #/admin/api/unstable/products/632910392.json
    requests.delete(base_url+f"/admin/api/unstable/products/{simple_product_id}.json") 
    requests.delete(base_url+f"/admin/api/unstable/products/{configurable_product_id}.json") 
​
    #delete customer 
    #/admin/api/unstable/customers/207119551.json
    requests.delete(base_url+f"/admin/api/unstable/customers/{customer_id}.json") 
​
   
    print('Xóa hết những thì thuộc về em')
time.sleep(20)
choice = input("Do you want to delete all data (Y/N):")
if choice == "Y" or choice == "y":
    deleteAllCreatedData()
