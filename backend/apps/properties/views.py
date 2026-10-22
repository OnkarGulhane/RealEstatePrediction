from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

SUPPORTED_LOCATIONS = [
    "Agra", "Ahmadnagar", "Ahmedabad", "Allahabad", "Aurangabad", "Badlapur", "Bangalore", "Belgaum",
    "Bhiwadi", "Bhiwandi", "Bhopal", "Bhubaneswar", "Chandigarh", "Chennai", "Coimbatore", "Dehradun",
    "Durgapur", "Ernakulam", "Faridabad", "Ghaziabad", "Goa", "Greater Noida", "Guntur", "Gurgaon",
    "Guwahati", "Gwalior", "Haridwar", "Hyderabad", "Indore", "Jabalpur", "Jaipur", "Jamshedpur",
    "Jodhpur", "Kalyan", "Kanpur", "Kochi", "Kolkata", "Kozhikode", "Lucknow", "Ludhiana",
    "Madurai", "Mangalore", "Mohali", "Mumbai", "Mysore", "Nagpur", "Nashik", "Navi Mumbai",
    "Navsari", "Nellore", "New Delhi", "Noida", "Palakkad", "Palghar", "Panchkula", "Patna",
    "Pondicherry", "Pune", "Raipur", "Rajahmundry", "Ranchi", "Satara", "Shimla", "Siliguri",
    "Solapur", "Sonipat", "Surat", "Thane", "Thrissur", "Tirupati", "Trichy", "Trivandrum",
    "Udaipur", "Udupi", "Vadodara", "Vapi", "Varanasi", "Vijayawada", "Visakhapatnam", "Vrindavan",
    "Zirakpur"
]

CATEGORICAL_METADATA = {
    "area_bases": ["CARPET", "SUPER"],
    "categories": {
        "furnishing": ["Furnished", "Semi-Furnished", "Unfurnished"],
        "transaction_type": ["New Property", "Resale", "Rent/Lease", "Other"],
        "status": ["Ready to Move"],
        "facing": ["East", "North", "North - East", "North - West", "South", "South - East", "South -West", "West"],
        "ownership": ["Freehold", "Co-operative Society", "Leasehold", "Power Of Attorney"]
    }
}


class LocationsMetadataView(APIView):
    """
    Public metadata endpoint returning canonical supported Indian cities and feature levels
    matching the trained regression model.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            "schema_version": "1.0",
            "total_locations": len(SUPPORTED_LOCATIONS),
            "locations": [
                {"name": loc, "normalized": loc.strip().lower()}
                for loc in SUPPORTED_LOCATIONS
            ],
            **CATEGORICAL_METADATA,
        })
