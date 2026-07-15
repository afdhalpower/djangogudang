from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction
from django.contrib.auth import get_user_model
from categories.models import Category
from units.models import Unit
from products.models import Product
from stock.models import StockTransaction, StockTransactionItem

User = get_user_model()

class StockTransactionTests(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(username="staff", password="password")
        
        # Create category & unit
        self.category = Category.objects.create(name="Electronics", status="active")
        self.unit = Unit.objects.create(name="Pieces", abbreviation="pcs", status="active")
        
        # Create product with initial stock
        self.product = Product.objects.create(
            sku="EL-PRO-01",
            name="Test Product",
            category=self.category,
            unit=self.unit,
            purchase_price=1000,
            selling_price=1500,
            current_stock=10,
            minimum_stock=5,
            status="active"
        )

    def test_stock_in_increases_stock(self):
        # Create stock in transaction
        tx = StockTransaction.objects.create(
            movement_type=StockTransaction.MOVEMENT_IN,
            reference_number="IN-001",
            created_by=self.user
        )
        # Add item
        item = StockTransactionItem.objects.create(
            transaction=tx,
            product=self.product,
            quantity=5,
            unit_price=1000
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.current_stock, 15)

    def test_stock_out_decreases_stock(self):
        # Create stock out transaction
        tx = StockTransaction.objects.create(
            movement_type=StockTransaction.MOVEMENT_OUT,
            reference_number="OUT-001",
            created_by=self.user
        )
        # Add item
        item = StockTransactionItem.objects.create(
            transaction=tx,
            product=self.product,
            quantity=4,
            unit_price=1500
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.current_stock, 6)

    def test_stock_out_insufficient_stock_raises_validation_error(self):
        # Create stock out transaction
        tx = StockTransaction.objects.create(
            movement_type=StockTransaction.MOVEMENT_OUT,
            reference_number="OUT-002",
            created_by=self.user
        )
        # Try to deduct 11 items when available is 10
        with self.assertRaises(ValidationError):
            with db_transaction.atomic():
                StockTransactionItem.objects.create(
                    transaction=tx,
                    product=self.product,
                    quantity=11,
                    unit_price=1500
                )
        
        # Verify stock remains unchanged
        self.product.refresh_from_db()
        self.assertEqual(self.product.current_stock, 10)

    def test_stock_adjustment_add_increases_stock(self):
        tx = StockTransaction.objects.create(
            movement_type=StockTransaction.MOVEMENT_ADJUSTMENT,
            reference_number="ADJ-001",
            adjustment_reason="correction",
            adjustment_direction="add",
            created_by=self.user
        )
        StockTransactionItem.objects.create(
            transaction=tx,
            product=self.product,
            quantity=3,
            unit_price=0
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.current_stock, 13)

    def test_stock_adjustment_remove_insufficient_raises_validation_error(self):
        tx = StockTransaction.objects.create(
            movement_type=StockTransaction.MOVEMENT_ADJUSTMENT,
            reference_number="ADJ-002",
            adjustment_reason="damaged",
            adjustment_direction="remove",
            created_by=self.user
        )
        with self.assertRaises(ValidationError):
            with db_transaction.atomic():
                StockTransactionItem.objects.create(
                    transaction=tx,
                    product=self.product,
                    quantity=15,
                    unit_price=0
                )
        self.product.refresh_from_db()
        self.assertEqual(self.product.current_stock, 10)
