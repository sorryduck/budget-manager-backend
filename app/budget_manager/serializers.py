from rest_framework import serializers
from .models import Expenses, Store, ExpensesCategory


class UserSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    budget = serializers.DecimalField(max_digits=15, decimal_places=2)

    
class CategorySerializer(serializers.Serializer):
    title = serializers.CharField()


class StoreSerializer(serializers.Serializer):
    title = serializers.CharField()


class ExpensesSerializer(serializers.Serializer):
    pk = serializers.IntegerField(required=False)
    date = serializers.DateField(required=False)
    title = serializers.CharField()
    category = CategorySerializer(required=False)
    store = StoreSerializer(required=False)
    price = serializers.DecimalField(max_digits=99, decimal_places=2, required=False)
    budget_id = serializers.IntegerField(required=False)

    def create(self, validated_data):
        return Expenses.objects.create(
            title=validated_data.get("title").capitalize(),
            date=validated_data.get('date'),
            budget_id=self.context.get('pk'),
            price=validated_data.get("price"),
            category=ExpensesCategory.objects.get_or_create(
                title=validated_data.get("category").get("title").capitalize()
            )[0],
            store=Store.objects.get_or_create(
                title=validated_data.get("store").get("title").capitalize()
            )[0],
        )
    

class CategorySumSerializer(serializers.Serializer):
    category__title = serializers.CharField()
    total_sum = serializers.DecimalField(max_digits=99, decimal_places=2)


class StoreSumSerializer(serializers.Serializer):
    store__title = serializers.CharField()
    total_sum = serializers.DecimalField(max_digits=99, decimal_places=2)


class ExpensesSumSerializer(serializers.Serializer):
    title = serializers.CharField()
    total_sum = serializers.DecimalField(max_digits=99, decimal_places=2)
