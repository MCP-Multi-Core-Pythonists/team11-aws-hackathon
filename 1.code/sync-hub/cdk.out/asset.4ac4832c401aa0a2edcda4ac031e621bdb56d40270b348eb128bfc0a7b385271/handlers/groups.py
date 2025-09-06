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

class GroupsHandler:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.groups_table = self.dynamodb.Table(os.environ['GROUPS_TABLE'])
        self.group_members_table = self.dynamodb.Table(os.environ['GROUP_MEMBERS_TABLE'])
    
    def handle(self, event: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
        method = event.get("requestContext", {}).get("http", {}).get("method")
        path = event.get("requestContext", {}).get("http", {}).get("path")
        
        if path == "/groups" and method == "GET":
            return self._list_groups(tenant_id)
        elif path == "/groups" and method == "POST":
            return self._create_group(event, tenant_id)
        elif path.startswith("/groups/") and method == "GET":
            group_id = path.split("/")[-1]
            if path.endswith("/members"):
                return self._list_group_members(group_id, tenant_id)
            else:
                return self._get_group(group_id, tenant_id)
        elif path.startswith("/groups/") and method == "PUT":
            group_id = path.split("/")[-1]
            return self._update_group(event, group_id, tenant_id)
        elif path.startswith("/groups/") and method == "DELETE":
            group_id = path.split("/")[-1]
            return self._delete_group(group_id, tenant_id)
        
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Not found"})
        }
    
    def _list_groups(self, tenant_id: str) -> Dict[str, Any]:
        try:
            response = self.groups_table.query(
                KeyConditionExpression=Key('tenant_id').eq(tenant_id)
            )
            
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"groups": response["Items"]}, cls=DecimalEncoder)
            }
        except Exception as e:
            print(f"Error listing groups: {e}")
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Internal server error"})
            }
    
    def _create_group(self, event: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
        try:
            body = json.loads(event.get("body", "{}"))
            group_id = str(uuid.uuid4())
            
            group = {
                "tenant_id": tenant_id,
                "group_id": group_id,
                "name": body.get("name"),
                "description": body.get("description", ""),
                "owner_id": tenant_id,
                "created_at": int(time.time()),
                "updated_at": int(time.time())
            }
            
            self.groups_table.put_item(Item=group)
            
            return {
                "statusCode": 201,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps(group, cls=DecimalEncoder)
            }
        except Exception as e:
            print(f"Error creating group: {e}")
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Internal server error"})
            }
    
    def _get_group(self, group_id: str, tenant_id: str) -> Dict[str, Any]:
        try:
            response = self.groups_table.get_item(
                Key={"tenant_id": tenant_id, "group_id": group_id}
            )
            
            if "Item" not in response:
                return {
                    "statusCode": 404,
                    "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                    "body": json.dumps({"error": "Group not found"})
                }
            
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps(response["Item"], cls=DecimalEncoder)
            }
        except Exception as e:
            print(f"Error getting group: {e}")
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Internal server error"})
            }
    
    def _update_group(self, event: Dict[str, Any], group_id: str, tenant_id: str) -> Dict[str, Any]:
        try:
            body = json.loads(event.get("body", "{}"))
            
            update_expression = "SET updated_at = :updated"
            expression_values = {":updated": int(time.time())}
            
            if "name" in body:
                update_expression += ", #name = :name"
                expression_values[":name"] = body["name"]
            
            if "description" in body:
                update_expression += ", description = :description"
                expression_values[":description"] = body["description"]
            
            self.groups_table.update_item(
                Key={"tenant_id": tenant_id, "group_id": group_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames={"#name": "name"} if "name" in body else None,
                ExpressionAttributeValues=expression_values
            )
            
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"message": "Group updated"})
            }
        except Exception as e:
            print(f"Error updating group: {e}")
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Internal server error"})
            }
    
    def _delete_group(self, group_id: str, tenant_id: str) -> Dict[str, Any]:
        try:
            self.groups_table.delete_item(
                Key={"tenant_id": tenant_id, "group_id": group_id}
            )
            
            return {
                "statusCode": 204,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": ""
            }
        except Exception as e:
            print(f"Error deleting group: {e}")
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Internal server error"})
            }
    
    def _list_group_members(self, group_id: str, tenant_id: str) -> Dict[str, Any]:
        try:
            response = self.group_members_table.query(
                KeyConditionExpression=Key('tenant_id').eq(tenant_id) & Key('group_id#user_id').begins_with(f"{group_id}#")
            )
            
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"members": response["Items"]}, cls=DecimalEncoder)
            }
        except Exception as e:
            print(f"Error listing group members: {e}")
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Internal server error"})
            }
