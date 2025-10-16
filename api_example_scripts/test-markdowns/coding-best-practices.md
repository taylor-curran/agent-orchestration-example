# Comprehensive Coding Best Practices Guide

## Table of Contents
1. [Code Organization](#code-organization)
2. [Naming Conventions](#naming-conventions)
3. [Function Design](#function-design)
4. [Error Handling](#error-handling)
5. [Documentation](#documentation)
6. [Testing](#testing)
7. [Performance](#performance)
8. [Security](#security)
9. [Code Review](#code-review)
10. [Version Control](#version-control)

## Code Organization

### Project Structure
Organize your project with a clear, logical structure:

```
project/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   ├── services/
│   ├── utils/
│   └── config/
├── tests/
├── docs/
├── requirements.txt
├── README.md
└── .gitignore
```

### Module Design Principles

#### Single Responsibility Principle
Each module should have one reason to change:

```python
# Good: Focused on user authentication
class UserAuthenticator:
    def authenticate(self, username, password):
        pass
    
    def validate_credentials(self, credentials):
        pass

# Bad: Mixed responsibilities
class UserManager:
    def authenticate(self, username, password):
        pass
    
    def send_email(self, user, message):
        pass
    
    def generate_report(self, users):
        pass
```

#### Dependency Injection
Make dependencies explicit and testable:

```python
# Good: Dependencies injected
class OrderService:
    def __init__(self, payment_processor, inventory_service):
        self.payment_processor = payment_processor
        self.inventory_service = inventory_service
    
    def process_order(self, order):
        if self.inventory_service.check_availability(order.items):
            return self.payment_processor.charge(order.total)

# Bad: Hard-coded dependencies
class OrderService:
    def process_order(self, order):
        payment_processor = StripePaymentProcessor()  # Hard to test
        inventory = DatabaseInventory()  # Hard to mock
        # ... rest of logic
```

## Naming Conventions

### Variables and Functions
Use descriptive, meaningful names:

```python
# Good
user_count = len(active_users)
def calculate_monthly_revenue(transactions):
    pass

# Bad
n = len(users)
def calc(data):
    pass
```

### Constants
Use UPPER_CASE for constants:

```python
# Good
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT_SECONDS = 30
API_BASE_URL = "https://api.example.com"

# Bad
maxRetries = 3
timeout = 30
```

### Classes
Use PascalCase for class names:

```python
# Good
class DatabaseConnection:
    pass

class UserAccountManager:
    pass

# Bad
class database_connection:
    pass

class useraccountmanager:
    pass
```

## Function Design

### Keep Functions Small
Functions should do one thing well:

```python
# Good: Small, focused function
def validate_email(email):
    """Validate email format using regex."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def send_welcome_email(user):
    """Send welcome email to new user."""
    if validate_email(user.email):
        email_service.send(user.email, "Welcome!", get_welcome_template())

# Bad: Function doing too many things
def process_new_user(user_data):
    # Validate email
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, user_data['email']):
        raise ValueError("Invalid email")
    
    # Create user
    user = User(user_data)
    database.save(user)
    
    # Send email
    email_service.send(user.email, "Welcome!", get_welcome_template())
    
    # Log activity
    logger.info(f"New user created: {user.id}")
    
    # Update metrics
    metrics.increment("users.created")
```

### Function Parameters
Limit the number of parameters:

```python
# Good: Use data classes or dictionaries for multiple parameters
from dataclasses import dataclass

@dataclass
class UserConfig:
    name: str
    email: str
    age: int
    preferences: dict

def create_user(config: UserConfig):
    pass

# Bad: Too many parameters
def create_user(name, email, age, country, city, phone, preferences, 
                notifications_enabled, theme, language):
    pass
```

### Return Values
Be consistent with return types:

```python
# Good: Consistent return types
def find_user(user_id: int) -> Optional[User]:
    user = database.get_user(user_id)
    return user if user else None

# Bad: Inconsistent return types
def find_user(user_id):
    user = database.get_user(user_id)
    if user:
        return user
    else:
        return False  # Should return None, not False
```

## Error Handling

### Use Specific Exceptions
Create custom exceptions for different error conditions:

```python
class ValidationError(Exception):
    """Raised when input validation fails."""
    pass

class DatabaseConnectionError(Exception):
    """Raised when database connection fails."""
    pass

class UserNotFoundError(Exception):
    """Raised when user lookup fails."""
    pass

# Usage
def get_user(user_id):
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValidationError(f"Invalid user ID: {user_id}")
    
    try:
        user = database.get_user(user_id)
    except ConnectionError as e:
        raise DatabaseConnectionError(f"Failed to connect to database: {e}")
    
    if not user:
        raise UserNotFoundError(f"User with ID {user_id} not found")
    
    return user
```

### Fail Fast Principle
Validate inputs early:

```python
# Good: Validate early
def calculate_discount(price, discount_percentage):
    if price < 0:
        raise ValueError("Price cannot be negative")
    if not 0 <= discount_percentage <= 100:
        raise ValueError("Discount must be between 0 and 100")
    
    return price * (discount_percentage / 100)

# Bad: Validate late or not at all
def calculate_discount(price, discount_percentage):
    # ... lots of processing ...
    result = price * (discount_percentage / 100)  # Could fail with invalid inputs
    return result
```

### Logging
Use structured logging with appropriate levels:

```python
import logging
import json

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def process_payment(order_id, amount):
    logger.info("Processing payment", extra={
        "order_id": order_id,
        "amount": amount,
        "action": "payment_start"
    })
    
    try:
        result = payment_gateway.charge(amount)
        logger.info("Payment successful", extra={
            "order_id": order_id,
            "transaction_id": result.transaction_id,
            "action": "payment_success"
        })
        return result
    except PaymentError as e:
        logger.error("Payment failed", extra={
            "order_id": order_id,
            "error": str(e),
            "action": "payment_failure"
        })
        raise
```

## Documentation

### Docstrings
Write comprehensive docstrings:

```python
def calculate_compound_interest(principal, rate, time, compound_frequency=1):
    """
    Calculate compound interest.
    
    Args:
        principal (float): The initial amount of money.
        rate (float): Annual interest rate as a decimal (e.g., 0.05 for 5%).
        time (float): Time period in years.
        compound_frequency (int, optional): Number of times interest is 
            compounded per year. Defaults to 1.
    
    Returns:
        float: The final amount after compound interest.
    
    Raises:
        ValueError: If any of the numeric inputs are negative.
    
    Example:
        >>> calculate_compound_interest(1000, 0.05, 2, 4)
        1104.89
    """
    if principal < 0 or rate < 0 or time < 0:
        raise ValueError("All inputs must be non-negative")
    
    return principal * (1 + rate / compound_frequency) ** (compound_frequency * time)
```

### Type Hints
Use type hints for better code clarity:

```python
from typing import List, Dict, Optional, Union
from datetime import datetime

def process_user_data(
    users: List[Dict[str, Union[str, int]]], 
    start_date: Optional[datetime] = None
) -> Dict[str, int]:
    """
    Process user data and return statistics.
    
    Args:
        users: List of user dictionaries containing user information.
        start_date: Optional start date for filtering users.
    
    Returns:
        Dictionary containing user statistics.
    """
    stats = {"total": 0, "active": 0, "inactive": 0}
    
    for user in users:
        stats["total"] += 1
        if user.get("last_login"):
            stats["active"] += 1
        else:
            stats["inactive"] += 1
    
    return stats
```

## Testing

### Unit Tests
Write comprehensive unit tests:

```python
import unittest
from unittest.mock import Mock, patch
from myapp.services import UserService
from myapp.exceptions import UserNotFoundError

class TestUserService(unittest.TestCase):
    def setUp(self):
        self.mock_database = Mock()
        self.user_service = UserService(self.mock_database)
    
    def test_get_user_success(self):
        # Arrange
        user_id = 123
        expected_user = {"id": 123, "name": "John Doe"}
        self.mock_database.get_user.return_value = expected_user
        
        # Act
        result = self.user_service.get_user(user_id)
        
        # Assert
        self.assertEqual(result, expected_user)
        self.mock_database.get_user.assert_called_once_with(user_id)
    
    def test_get_user_not_found(self):
        # Arrange
        user_id = 999
        self.mock_database.get_user.return_value = None
        
        # Act & Assert
        with self.assertRaises(UserNotFoundError):
            self.user_service.get_user(user_id)
    
    @patch('myapp.services.logger')
    def test_get_user_logs_access(self, mock_logger):
        # Arrange
        user_id = 123
        self.mock_database.get_user.return_value = {"id": 123}
        
        # Act
        self.user_service.get_user(user_id)
        
        # Assert
        mock_logger.info.assert_called_with(f"Accessing user {user_id}")
```

### Integration Tests
Test component interactions:

```python
import pytest
from myapp import create_app
from myapp.database import init_db

@pytest.fixture
def app():
    app = create_app(testing=True)
    with app.app_context():
        init_db()
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_create_user_endpoint(client):
    # Test successful user creation
    response = client.post('/users', json={
        'name': 'John Doe',
        'email': 'john@example.com'
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == 'John Doe'
    assert 'id' in data

def test_create_user_invalid_email(client):
    # Test validation error
    response = client.post('/users', json={
        'name': 'John Doe',
        'email': 'invalid-email'
    })
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
```

## Performance

### Algorithm Complexity
Choose appropriate algorithms:

```python
# Good: O(n) time complexity
def find_duplicates_efficient(numbers):
    """Find duplicates using a set for O(n) time complexity."""
    seen = set()
    duplicates = set()
    
    for num in numbers:
        if num in seen:
            duplicates.add(num)
        else:
            seen.add(num)
    
    return list(duplicates)

# Bad: O(n²) time complexity
def find_duplicates_slow(numbers):
    """Find duplicates using nested loops - O(n²) time complexity."""
    duplicates = []
    
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            if numbers[i] == numbers[j] and numbers[i] not in duplicates:
                duplicates.append(numbers[i])
    
    return duplicates
```

### Memory Management
Be mindful of memory usage:

```python
# Good: Generator for memory efficiency
def read_large_file_lines(filename):
    """Read file line by line using generator."""
    with open(filename, 'r') as file:
        for line in file:
            yield line.strip()

# Usage
for line in read_large_file_lines('huge_file.txt'):
    process_line(line)

# Bad: Loading entire file into memory
def read_large_file_all(filename):
    """Read entire file into memory - not suitable for large files."""
    with open(filename, 'r') as file:
        return file.readlines()  # Could consume too much memory
```

### Caching
Implement caching for expensive operations:

```python
from functools import lru_cache
import time

@lru_cache(maxsize=128)
def expensive_calculation(n):
    """Expensive calculation with caching."""
    time.sleep(1)  # Simulate expensive operation
    return n * n * n

# Usage
result1 = expensive_calculation(10)  # Takes 1 second
result2 = expensive_calculation(10)  # Returns immediately from cache
```

## Security

### Input Validation
Always validate and sanitize inputs:

```python
import re
from html import escape

def validate_username(username):
    """Validate username format and length."""
    if not username or len(username) < 3 or len(username) > 20:
        raise ValueError("Username must be 3-20 characters long")
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise ValueError("Username can only contain letters, numbers, and underscores")
    
    return username

def sanitize_html_input(user_input):
    """Sanitize HTML input to prevent XSS attacks."""
    return escape(user_input)

# Usage
try:
    clean_username = validate_username(user_input)
    safe_comment = sanitize_html_input(comment_input)
except ValueError as e:
    return {"error": str(e)}
```

### SQL Injection Prevention
Use parameterized queries:

```python
import sqlite3

# Good: Parameterized query
def get_user_by_email(email):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    conn.close()
    return user

# Bad: String concatenation (vulnerable to SQL injection)
def get_user_by_email_unsafe(email):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # NEVER do this - vulnerable to SQL injection
    query = f"SELECT * FROM users WHERE email = '{email}'"
    cursor.execute(query)
    user = cursor.fetchone()
    
    conn.close()
    return user
```

### Environment Variables
Store sensitive configuration in environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Good: Use environment variables for sensitive data
DATABASE_URL = os.getenv('DATABASE_URL')
API_SECRET_KEY = os.getenv('API_SECRET_KEY')
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')

if not all([DATABASE_URL, API_SECRET_KEY, ENCRYPTION_KEY]):
    raise ValueError("Missing required environment variables")

# Bad: Hard-coded secrets
DATABASE_URL = "postgresql://user:password@localhost/db"  # Never do this
API_SECRET_KEY = "super-secret-key-123"  # Never do this
```

## Code Review

### Review Checklist
- **Functionality**: Does the code work as intended?
- **Readability**: Is the code easy to understand?
- **Performance**: Are there any performance bottlenecks?
- **Security**: Are there any security vulnerabilities?
- **Testing**: Are there adequate tests?
- **Documentation**: Is the code properly documented?

### Review Comments
Provide constructive feedback:

```python
# Good review comment:
# "Consider using a dictionary lookup instead of multiple if-elif statements 
# for better performance and readability. For example:
# 
# status_messages = {
#     'pending': 'Order is being processed',
#     'shipped': 'Order has been shipped',
#     'delivered': 'Order has been delivered'
# }
# return status_messages.get(status, 'Unknown status')"

# Bad review comment:
# "This is wrong, fix it."
```

## Version Control

### Commit Messages
Write clear, descriptive commit messages:

```bash
# Good commit messages
git commit -m "feat: add user authentication with JWT tokens"
git commit -m "fix: resolve memory leak in data processing pipeline"
git commit -m "docs: update API documentation with new endpoints"
git commit -m "refactor: extract email validation into separate utility"

# Bad commit messages
git commit -m "fix stuff"
git commit -m "updates"
git commit -m "wip"
```

### Branch Strategy
Use a consistent branching strategy:

```bash
# Feature branches
git checkout -b feature/user-authentication
git checkout -b feature/payment-integration

# Bug fix branches
git checkout -b bugfix/memory-leak-fix
git checkout -b hotfix/security-patch

# Release branches
git checkout -b release/v1.2.0
```

### Pull Request Guidelines
- Keep PRs focused and small
- Include a clear description of changes
- Add tests for new functionality
- Update documentation as needed
- Request reviews from relevant team members

## Conclusion

Following these coding best practices will lead to:
- **Maintainable code**: Easier to modify and extend
- **Reliable software**: Fewer bugs and better error handling
- **Team productivity**: Consistent standards improve collaboration
- **Scalable systems**: Well-designed code handles growth better
- **Security**: Proper practices prevent vulnerabilities

Remember: Good code is not just working code—it's code that others (including your future self) can easily understand, modify, and maintain.

## Additional Resources

- [Clean Code by Robert C. Martin](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882)
- [The Pragmatic Programmer](https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/)
- [Python PEP 8 Style Guide](https://pep8.org/)
- [Google Style Guides](https://google.github.io/styleguide/)
- [OWASP Security Guidelines](https://owasp.org/)
