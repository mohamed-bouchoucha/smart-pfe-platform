from django.contrib.auth import get_user_model
User = get_user_model()

# Create Admin User
if not User.objects.filter(email='admin@smartpfe.com').exists():
    User.objects.create_superuser(
        email='admin@smartpfe.com',
        username='admin',
        password='adminpass',
        first_name='Admin',
        last_name='SmartPFE',
        role='admin'
    )
    print("Admin user created.")
else:
    u = User.objects.get(email='admin@smartpfe.com')
    u.set_password('adminpass')
    u.role = 'admin'
    u.save()
    print("Admin user updated.")

# Create Student User
if not User.objects.filter(email='mohamed.b@example.com').exists():
    User.objects.create_user(
        email='mohamed.b@example.com',
        username='mohamed.b',
        password='password123',
        first_name='Mohamed',
        last_name='Bouchoucha',
        role='student'
    )
    print("Student user created.")
else:
    u = User.objects.get(email='mohamed.b@example.com')
    u.set_password('password123')
    u.role = 'student'
    u.save()
    print("Student user updated.")
