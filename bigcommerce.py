# import copy
# import io
import time
from urllib.request import Request, urlopen
import re
#
# import pytz
#import xmltodict
import json
#import requests
# from PIL import Image
# from PIL import ImageFile
import requests
# from datasync.libs.errors import Errors
from datasync.libs.response import Response
# from datasync.libs.utils import get_random_useragent
# from datasync.libs.tracking_company import TrackingCompany
from datasync.libs.utils import *
from datasync.models.channel import ModelChannel
# from datasync.models.constructs.category import CatalogCategory
# from datasync.models.constructs.order import Order, OrderProducts, OrderItemOption, OrderHistory, OrderAddress, OrderAddressCountry
from datasync.models.constructs.product import Product, ProductImage, ProductAttribute, ProductVariant,ProductVariantAttribute,ProductVideo, ProductLocation
# import dateutil.relativedelta

class ModelChannelsBigcommerce(ModelChannel):
	def __init__(self):
		super().__init__()

	def get_api_info(self):
		return {
            "shop": "feftahge1k",
			"password":"cbuhm850j22gldn2gjx5zxxzma2i1v3"
		}

	def display_setup_channel(self, data = None):
		parent = super().display_setup_channel(data)
		if parent.result != Response().SUCCESS:
			return parent
		bigcommerce = self.api("/v2/store")

		return Response().success()

	def set_channel_identifier(self):
		parent = super().set_channel_identifier()
		if parent.result != Response().SUCCESS:
			return parent
		self.set_identifier(self._state.channel.config.api.shop)
		return Response().success()

	def api(self,path, data = None,method = 'get'):
		url = "https://api.bigcommerce.com/stores/" + self._state.channel.config.api.shop + path
		header = {
			"Content-Type": "application/json",
			"X-Auth-Token": self._state.channel.config.api.password,
			"User-Agent": get_random_useragent(),
			"Accept": "application/json"
		}


		bigc_response = requests.request(method,url,headers = header,data = data)
		self._last_header = bigc_response.headers
		self._last_status = bigc_response.status_code


		return bigc_response.text

	def display_pull_channel(self):
		parent = super().display_pull_channel()
		if parent.result != Response().SUCCESS:
			return parent
		if self.is_product_process():
			self._state.pull.process.products.error = 0
			self._state.pull.process.products.imported = 0
			self._state.pull.process.products.new_entity = 0
			self._state.pull.process.products.total = 0

			# self._state.pull.process.products.total =?
			product_api = self.api("/v3/catalog/products")
			self._state.pull.process.products.total = json.loads(product_api)['meta']['pagination']['total']

		if self.is_order_process():
			self._state.pull.process.orders.total = 0
			self._state.pull.process.orders.imported = 0
			self._state.pull.process.orders.new_entity = 0
			self._state.pull.process.orders.error = 0
			self._state.pull.process.orders.id_src = 0

			# /stores/{store_hash}/v2/orders
			order_api = self.api("/v2/orders")
			self._state.pull.process.orders.total = len(list(order_api.text))

		if self.is_category_process():
			self._state.pull.process.categories.total = 0
			self._state.pull.process.categories.imported = 0
			self._state.pull.process.categories.new_entity = 0
			self._state.pull.process.categories.error = 0
			category_api = self.api("/v3/catalog/categories")
			# /stores/{store_hash}/v3/catalog/categories
			self._state.pull.process.categories.total = json.loads(category_api)['meta']['pagination']['total']

		return Response().success()

	def get_products_main_export(self):
		products = self.api("/v3/catalog/products")
		return Response().success(data = json.loads(products)['data'])

	def get_products_ext_export(self, products):
		products = self.api("/v3/catalog/products")
		product_list = json.loads(products)['data']
		extend = dict()
		for p in product_list:
			product_id = p['id']
			extend[to_str(product_id)] = {'meta': [], 'media': [{}], 'category': None}

		return Response().success(extend)



	def get_product_id_import(self, convert: Product, product, products_ext):
		return product.id

	def check_product_import(self, product_id, convert: Product):
		product_list = json.loads(self.api("/v3/catalog/products"))['data']
		key_to_find = "sku"
		value_to_find = convert.sku
		result = [item for item in product_list if item.get(key_to_find) == value_to_find]
		if len(result) == 0:
			return False
		else:
			return str(result[0]["id"])



	def product_import(self, convert: Product, product, products_ext):

		#xu ly category
		categories_name =  product['category_name_list']
		category_ids = list()
		category_response = self.api("/v3/catalog/categories")
		category_list = json.loads(category_response)['data']
		category_name_list = [item['name'] for item in category_list]

		for category in category_list:
			if category['name'] in categories_name:
				category_ids.append(category['id'])

		for category_name in categories_name:
			if category_name not in category_name_list:
				category_data = {
					  "parent_id": 0,
					  "name": category_name,
					  "page_title": category_name
					}
				category_response = self.api("/v3/catalog/categories", data = json_encode(category_data),method = 'post')
				category_ids.append(json.loads(category_response)['data'][0]['id'])

		shopify_product_category = product.shopify_product_category

		#xu ly product type
		taxonomy_number = int(re.search(r'\d+', shopify_product_category).group())
		if taxonomy_number < 4342 or taxonomy_number > 4376:
			product_type = "physical"
		else:
			product_type = "digital"

		#du lieu san pham
		product_data = {
		  "name": product.name,
		  "type": product_type,
		  "sku": product.sku,
		  "description": product.description,
		  "weight": product.weight,
		  # "width": 9999999999,
		  # "depth": 9999999999,
		  # "height": 9999999999,
		  "price": product.price,
		  "cost_price": product.cost,
		  "retail_price": product.price,
		  "sale_price": product.special_price["price"],
		  "categories": category_ids,
		  "brand_name": product.brand,
		  "inventory_level": product.qty,
		  "inventory_tracking": "variant",
		  "is_visible": product.channel["channel_1"]["visible"],
		  "condition": product.condition.capitalize(),
		  "meta_keywords": list(product.meta_keyword),
		  "variants": [
		    {
		      "cost_price": 0,
		      "price": 0,
		      "sale_price": 0,
		      "retail_price": 0,
		      "weight": 0,
		      "width": 0,
		      "height": 0,
		      "depth": 0,
		      "is_free_shipping": True,
		      "fixed_cost_shipping_price": 0,
		      "purchasing_disabled": True,
		      "purchasing_disabled_message": "string",
		      "upc": "string",
		      "inventory_level": 2147483647,
		      "inventory_warning_level": 2147483647,
		      "bin_picking_number": "string",
		      "mpn": "string",
		      "gtin": "012345678905",
		      "product_id": 0,
		      "option_values": [
		        {
		          "option_display_name": "Color",
		          "label": "Beige"
		        }
		      ],
		      "calculated_price": 0,
		      "calculated_weight": 0
		    }
		  ]
		}

		#xu ly variant
		product_variants = product.variants
		variants_data = list()
		count = 0
		for variant in product_variants:
			option_values = list()
			for attr in variant["attributes"]:
				option_values.append({
						"option_display_name": attr["attribute_name"],
						"label": attr["attribute_value_name"]
					})
			if count == 0:
				sku = variant["sku"] + "mainsku"
			else:
				sku = variant["sku"]
			variants_data.append({
				"price": variant["price"],
				"weight": variant["weight"],
				"inventory_level": variant["qty"],
				"sku": sku,
				"option_values": option_values,
				"thumb_image":variant["thumb_image"]
			})
			count = count + 1
		product_data["variants"] = variants_data

		#check product exist:
		created_product = self.api("/v3/catalog/products", data = json.dumps(product_data), method = "post")
		time.sleep(5)
		created_product_id = json.loads(created_product)['data']['id']

		#xu ly anh
		img_list = list()
		thumb_image_data = {
				"image_url": product.thumb_image["url"],
				"product_id": created_product_id,
				"is_thumbnail": True,
				"sort_order":  product.thumb_image["position"]
			}
		img_list.append(thumb_image_data)
		for img in product.images:
			position = img["url"].find(".jpg")

			# Check if ".jpg" is found, and if so, slice the string to remove everything after ".jpg"
			if position != -1:
				modified_url = img["url"][:position + 4]  # +4 to include the ".jpg"
			else:
				modified_url = img["url"]

			img_list.append({
				"image_url": modified_url,
				"product_id": created_product_id,
				"sort_order": img["position"]
			})
		for img in img_list:
			try:
				del img["image_id"]
			except:
				pass
			image_import = self.api("/v3/catalog/products/"+str(created_product_id)+"/images", data = json.dumps(img), method = "post")
			print(image_import)
		created_variants = self.api("/v3/catalog/products/"+str(created_product_id)+"/variants")
		time.sleep(5)

		for variant in json.loads(created_variants)['data']:
			#update channel 2
			ware_house_vars = product.variants
			key_to_find = "sku"
			value_to_find = variant["sku"].replace("mainsku", "")
			result = next((d for d in ware_house_vars if d.get(key_to_find) == value_to_find), None)
			self.insert_map_product(result,result["_id"],variant["id"])
			#update anh variant
			for v in variants_data:
				if variant["sku"].replace("mainsku", "") == v["sku"] or variant["sku"] == v["sku"]:

					variant_image_url = v["thumb_image"]["url"]
					img_import = self.api("/v3/catalog/products/"+str(created_product_id)+"/variants/"+str(variant["id"])+"/image", data =json.dumps({"image_url":variant_image_url}), method = "post")

		return Response().success(created_product_id)

	def product_channel_import(self, convert: Product, product, products_ext):
		return self.product_import(convert, product, products_ext)


	def product_channel_update(self, product_id, product: Product, products_ext):

		product_variants = self.get_variants(product,1)
		product["variants"] = product_variants
		if product.is_variant == False:
			product_list = json.loads(self.api("/v3/catalog/products"))['data']
			key_to_find = "sku"
			value_to_find = product.sku
			result = [item for item in product_list if item.get(key_to_find) == value_to_find]
			if len(result) == 0:
				product["id"] = product_id
				product_data = product
				product_data["type"] = "physical"
				product_data["condition"] = "New"
				update_response = self.api("/v3/catalog/products/" + str(product_id), data = json.dumps(product_data), method = "put")
				return Response().success(product_id)

			product_data = result[0]


			data_push = {key: product[key] if key in product else value for key, value in product_data.items()}

			# Update dict1 with the updated_dict
			product_data.update(data_push)
			product_data["type"] = "physical"
			product_data["condition"] = "New"
			product_data["id"] = product_id

			# xu ly variant
			last_variants = json.loads(self.api("/v3/catalog/products/"+str(product_id)+"/variants"))["data"]
			variants_data = list()
			count = 0
			for variant in product_variants:
				for var in last_variants:
					if int(variant["channel"]["channel_2"]["product_id"]) == var["id"]:
						print(var["id"])
						option_values = list()
						for attr in variant["attributes"]:
							option_values.append({
								"option_display_name": attr["attribute_name"],
								"label": attr["attribute_value_name"]
							})
						if count == 0:
							sku_var = var["sku"] + "main"
						else:
							sku_var = var["sku"]
						variants_data.append({
							"id": var["id"],
							"sku": sku_var,
							"price": variant["price"],
							"weight": variant["weight"],
							"inventory_level": variant["qty"],
							"option_values": option_values,
							"image_url": variant["thumb_image"]["url"]
						})

				count = count + 1


			for variant in variants_data:
				update_var_response = self.api("/v3/catalog/products/" + str(product_id)+"/variants/"+str(variant["id"]), data = json.dumps(variant), method = "put")
				print(update_var_response)
			product_data["variants"] = variants_data
			update_response = self.api("/v3/catalog/products/"+str(product_id),data = json.dumps(product_data),method = "put")
		return Response().success(product_id)


	# def insert_map_product(self, product, product_id, product_channel_id, **kwargs):
	# 	update_data = {"channel":{"channel_2":{"product_id":str(product_id)}}}
	# 	self.get_model_catalog().update(product["_id"], update_data)
	#
	#
	# 	return Response().success()