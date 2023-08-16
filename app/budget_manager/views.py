from .models import Expenses, AppUser, ExpensesCategory
from .serializers import *
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from django.db import transaction
from django.db.models import F, Sum
from rest_framework.pagination import PageNumberPagination
from rest_framework import status


class TableData(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Return response with expenses data filtered by user pk and paginated
        """

        paginator = PageNumberPagination()
        paginator.page_size = 10

        user_expenses = paginator.paginate_queryset(
            Expenses.objects.filter(budget=request.user.pk).order_by("-pk"), request
        )

        return Response(
            data={
                "content": ExpensesSerializer(user_expenses, many=True).data,
                "categories": CategorySerializer(
                    ExpensesCategory.objects.filter(
                        expenses__in=user_expenses
                    ).distinct(),
                    many=True,
                ).data,
                "stores": StoreSerializer(
                    Store.objects.filter(expenses__in=user_expenses).distinct(),
                    many=True,
                ).data,
                "pages": paginator.page.paginator.num_pages,
            }
        )

    @transaction.atomic
    def put(self, request):
        """
        Update expenses item in table
        """

        expenses_serializer_to_update = ExpensesSerializer(data=request.data)
        
        if expenses_serializer_to_update.is_valid():
            data = expenses_serializer_to_update.validated_data

            expenses_object_to_update = Expenses.objects.get(pk=data.get("pk"))

            expenses_object_to_update.title = data.get("title").capitalize()
            expenses_object_to_update.price = data.get("price")
            expenses_object_to_update.date = data.get("date")

            expenses_object_to_update.category.title = (
                data.get("category").get("title").capitalize()
            )
            expenses_object_to_update.category.save()

            expenses_object_to_update.store.title = (
                data.get("store").get("title").capitalize()
            )
            expenses_object_to_update.store.save()

            expenses_object_to_update.save()

            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def patch(self, request):
        """
        Change user budget
        """
        
        user_serializer = UserSerializer(data=request.data)

        if user_serializer.is_valid():
            AppUser.objects.filter(pk=request.user.pk).update(
                budget=user_serializer.validated_data.get("budget")
            )

            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def post(self, request):
        """
        Input new expenses item in the table
        """
        
        expenses_serializer = ExpensesSerializer(
            data=request.data, context={"pk": request.user.pk}
        )

        if expenses_serializer.is_valid():
            expenses_serializer.save()

            AppUser.objects.filter(pk=request.user.pk).update(
                budget=F("budget") - expenses_serializer.validated_data.get("price")
            )

            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def delete(self, request):
        """
        Delete expenses item from the table
        """

        expenses_object = Expenses.objects.get(pk=request.data.get("pk"))

        AppUser.objects.filter(pk=request.user.pk).update(
            budget=F("budget") + expenses_object.price
        )

        expenses_object.delete()

        return Response(status=status.HTTP_200_OK)


class UserData(APIView):
    """
    Gets information about user
    """
    
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(
            UserSerializer(AppUser.objects.get(pk=request.user.pk)).data,
        )


class StatisticData(APIView):
    """
    Gather information for statistic visualization
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        category_data = CategorySumSerializer(
            Expenses.objects.filter(budget_id=request.user.pk)
            .values("category__title")
            .annotate(total_sum=Sum("price")),
            many=True,
        ).data

        store_data = StoreSumSerializer(
            Expenses.objects.filter(budget_id=request.user.pk)
            .values("store__title")
            .annotate(total_sum=Sum("price")),
            many=True,
        ).data
        
        expenses_data = ExpensesSumSerializer(
            Expenses.objects.filter(budget_id=request.user.pk)
            .values("title")
            .annotate(total_sum=Sum("price")),
            many=True,
        ).data

        return Response(
            data={
                "category_data": {
                    "categories": [item["category__title"] for item in category_data],
                    "values": [item["total_sum"] for item in category_data],
                },
                "store_data": {
                    "stores": [item["store__title"] for item in store_data],
                    "values": [item["total_sum"] for item in store_data],
                },
                "expenses_data": {
                    "titles": [item["title"] for item in expenses_data],
                    "values": [item["total_sum"] for item in expenses_data],
                },
            }
        )
