import json
import os
import uuid
import time
from typing import Dict, Any
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

class SettingsHandler:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.settings_table = self.dynamodb.Table(os.environ['SETTINGS_TABLE'])
    
    def handle(self, event: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
        method = event.get("requestContext", {}).get("http", {}).get("method")
        path = event.get("requestContext", {}).get("http", {}).get("path")
        
        if path == "/settings" and method == "GET":
            return self._list_settings(tenant_id)
        elif path == "/settings" and method == "POST":
            return self._create_setting(event, tenant_id)
        elif path == "/settings/public" and method == "GET":
            return self._list_public_settings()
        elif path.startswith("/settings/") and method == "GET":
            setting_id = path.split("/")[-1]
            return self._get_setting(setting_id, tenant_id)
        elif path.startswith("/settings/") and method == "PUT":
            setting_id = path.split("/")[-1]
            if path.endswith("/visibility"):
                return self._update_visibility(event, setting_id, tenant_id)
            else:
                return self._update_setting(event, setting_id, tenant_id)
        elif path.startswith("/settings/") and method == "DELETE":
            setting_id = path.split("/")[-1]
            return self._delete_setting(setting_id, tenant_id)
        
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Not found"})
        }
    
    def _list_settings(self, tenant_id: str) -> Dict[str, Any]:
        try:
            response = self.settings_table.query(
                KeyConditionExpression=Key('tenant_id').eq(tenant_id)
            )
            
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"settings": response["Items"]}, cls=DecimalEncoder)
            }
        except Exception as e:
            print(f"Error listing settings: {e}")
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Internal server error"})
            }
    
    def _create_setting(self, event: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
        try:
            body = json.loads(event.get("body", "{}"))
            setting_id = str(uuid.uuid4())
            
            setting = {
                "tenant_id": tenant_id,
                "setting_id": setting_id,
                "name": body.get("name"),
                "value": body.get("value"),
                "is_public": body.get("is_public", False),
                "version": 1,
                "created_at": int(time.time()),
                "updated_at": int(time.time())
            }
            
            self.settings_table.put_item(Item=setting)
            
            return {
                "statusCode": 201,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps(setting, cls=DecimalEncoder)
            }
        except Exception as e:
            print(f"Error creating setting: {e}")
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Internal server error"})
            }
    
    def _get_setting(self, setting_id: str, tenant_id: str) -> Dict[str, Any]:
        try:
            response = self.settings_table.get_item(
                Key={"tenant_id": tenant_id, "setting_id": setting_id}
            )
            
            if "Item" not in response:
                return {
                    "statusCode": 404,
                    "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                    "body": json.dumps({"error": "Setting not found"})
                }
            
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps(response["Item"], cls=DecimalEncoder)
            }
        except Exception as e:
            print(f"Error getting setting: {e}")
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Internal server error"})
            }
    
    def _update_setting(self, event: Dict[str, Any], setting_id: str, tenant_id: str) -> Dict[str, Any]:
        try:
            body = json.loads(event.get("body", "{}"))
            
            update_expression = "SET updated_at = :updated"
            expression_values = {":updated": int(time.time())}
            
            if "name" in body:
                update_expression += ", #name = :name"
                expression_values[":name"] = body["name"]
            
            if "value" in body:
                update_expression += ", #value = :value"
                expression_values[":value"] = body["value"]
            
            self.settings_table.update_item(
                Key={"tenant_id": tenant_id, "setting_id": setting_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames={"#name": "name", "#value": "value"} if "name" in body or "value" in body else None,
                ExpressionAttributeValues=expression_values
            )
            
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"message": "Setting updated"})
            }
        except Exception as e:
            print(f"Error updating setting: {e}")
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Internal server error"})
            }
    
    def _delete_setting(self, setting_id: str, tenant_id: str) -> Dict[str, Any]:
        try:
            self.settings_table.delete_item(
                Key={"tenant_id": tenant_id, "setting_id": setting_id}
            )
            
            return {
                "statusCode": 204,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": ""
            }
        except Exception as e:
            print(f"Error deleting setting: {e}")
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Internal server error"})
            }
    
    def _update_visibility(self, event: Dict[str, Any], setting_id: str, tenant_id: str) -> Dict[str, Any]:
        try:
            body = json.loads(event.get("body", "{}"))
            is_public = body.get("is_public", False)
            
            self.settings_table.update_item(
                Key={"tenant_id": tenant_id, "setting_id": setting_id},
                UpdateExpression="SET is_public = :public, updated_at = :updated",
                ExpressionAttributeValues={
                    ":public": is_public,
                    ":updated": int(time.time())
                }
            )
            
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"is_public": is_public})
            }
        except Exception as e:
            print(f"Error updating visibility: {e}")
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Internal server error"})
            }
    
    def _list_public_settings(self) -> Dict[str, Any]:
        try:
            response = self.settings_table.scan(
                FilterExpression="is_public = :public",
                ExpressionAttributeValues={":public": True}
            )
            
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"settings": response["Items"]}, cls=DecimalEncoder)
            }
        except Exception as e:
            print(f"Error listing public settings: {e}")
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Internal server error"})
            }
