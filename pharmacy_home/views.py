# pharmacy_home/views.py
# Homepage view — passes all content data to the template

from django.shortcuts import render


def homepage(request):
    """
    Main landing page at http://localhost:8000/
    All section content is passed as context — easy to edit.
    """

    # ── Trust bar scrolling items ──
    trust_items = [
        "Medicine Inventory Management",
        "Smart Billing System",
        "eSewa Payment Integration",
        "Low Stock Alerts",
        "Sales Reports & Analytics",
        "Role-Based Access Control",
        "Expiry Date Tracking",
        "Multi-User Support",
    ]

    # ── Features section ──
    features = [
        {
            'icon':  'capsule-pill',
            'title': 'Medicine Inventory',
            'desc':  'Add, edit, and track all medicines with stock quantity, expiry dates, and low-stock alerts in real time.',
            'bg':    '#e0f2fe',
            'color': '#0ea5e9',
        },
        {
            'icon':  'receipt-cutoff',
            'title': 'Smart Billing',
            'desc':  'Create bills with multiple medicines in one transaction. Auto-calculates totals and reduces stock instantly.',
            'bg':    '#dcfce7',
            'color': '#16a34a',
        },
        {
            'icon':  'credit-card',
            'title': 'eSewa Integration',
            'desc':  'Accept secure digital payments via eSewa. Customers can pay online — fully integrated with order tracking.',
            'bg':    '#f3e8ff',
            'color': '#9333ea',
        },
        {
            'icon':  'bar-chart-line',
            'title': 'Sales Reports',
            'desc':  'View daily, weekly, and monthly revenue charts. See top-selling medicines and total earnings at a glance.',
            'bg':    '#fef9c3',
            'color': '#ca8a04',
        },
        {
            'icon':  'people',
            'title': 'Role-Based Access',
            'desc':  'Admin has full control. Pharmacists can bill and view inventory. Secure login for each role.',
            'bg':    '#fee2e2',
            'color': '#dc2626',
        },
        {
            'icon':  'cart3',
            'title': 'Online Cart & Orders',
            'desc':  'Customers can browse medicines, add to cart, and place orders with eSewa or cash on delivery.',
            'bg':    '#e0f2fe',
            'color': '#0284c7',
        },
    ]

    # ── How it works steps ──
    steps = [
        {
            'icon':  'person-plus',
            'title': 'Create Your Account',
            'desc':  'Sign up and set up your pharmacy profile in under 2 minutes.',
        },
        {
            'icon':  'capsule',
            'title': 'Add Medicines',
            'desc':  'Add your medicine inventory with prices, stock and expiry dates.',
        },
        {
            'icon':  'receipt',
            'title': 'Start Billing',
            'desc':  'Create bills, accept eSewa payments, and manage orders seamlessly.',
        },
        {
            'icon':  'graph-up-arrow',
            'title': 'Track & Grow',
            'desc':  'Monitor sales reports and make data-driven decisions for growth.',
        },
    ]

    # ── Stats banner ──
    stats = [
        {'num': '500+',  'label': 'Pharmacies Using PharmaCare'},
        {'num': '50K+',  'label': 'Bills Generated'},
        {'num': '99.9%', 'label': 'System Uptime'},
        {'num': '24/7',  'label': 'Customer Support'},
    ]

    # ── Testimonials ──
    testimonials = [
        {
            'text':    'PharmaCare completely transformed how we run our pharmacy. Billing used to take 10 minutes per customer, now it takes under a minute.',
            'name':    'Ramesh Shrestha',
            'role':    'Owner, Shrestha Pharmacy, Kathmandu',
            'initial': 'RS',
        },
        {
            'text':    'The eSewa integration is flawless. Our customers love being able to pay digitally, and the inventory alerts save us from running out of stock.',
            'name':    'Sunita Tamang',
            'role':    'Pharmacist, MedPlus Pharmacy, Pokhara',
            'initial': 'ST',
        },
        {
            'text':    'The dashboard reports give me a clear picture of daily sales. I can finally make informed decisions about which medicines to stock more of.',
            'name':    'Bikash Adhikari',
            'role':    'Manager, CityMed Pharmacy, Lalitpur',
            'initial': 'BA',
        },
    ]

    # ── Pricing plans ──
    pricing = [
        {
            'name':     'Starter',
            'price':    'Free',
            'desc':     'Perfect for small pharmacies just getting started.',
            'featured': False,
            'cta':      'Get Started',
            'features': [
                '1 Pharmacist Account',
                'Medicine Inventory',
                'Basic Billing',
                'Email Support',
            ],
        },
        {
            'name':     'Professional',
            'price':    '999',
            'desc':     'Everything a growing pharmacy needs.',
            'featured': True,
            'cta':      'Start Free Trial',
            'features': [
                '5 Staff Accounts',
                'Full Inventory Management',
                'eSewa Integration',
                'Sales Reports & Analytics',
                'Low Stock Alerts',
                'Priority Support',
            ],
        },
        {
            'name':     'Enterprise',
            'price':    '2,499',
            'desc':     'For pharmacy chains and large operations.',
            'featured': False,
            'cta':      'Contact Us',
            'features': [
                'Unlimited Accounts',
                'Multi-Branch Support',
                'Advanced Reports',
                'API Access',
                'Dedicated Support',
            ],
        },
    ]

    return render(request, 'pharmacy_home/homepage.html', {
        'trust_items':  trust_items,
        'features':     features,
        'steps':        steps,
        'stats':        stats,
        'testimonials': testimonials,
        'pricing':      pricing,
    })