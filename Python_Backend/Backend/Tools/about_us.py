from langchain_core.tools import Tool

def about_us_tool(_: str = "") -> str:
    """Provides information about Merry's Way Coffee including mission, story, specialties, and delivery zones."""
    return """
Merry's Way Coffee
Location: Koregaon Park, Pune
Founded: 2015

Story:
Founded in 2015, Merry’s Way started as a small family-owned café with one mission: to share the love of quality, ethically-sourced coffee with the community. Merry's journey across South America led to partnerships with small farms and cooperatives. Beans are roasted in-house to reflect regional flavors.

Mission:
To provide quality, ethically-sourced coffee while fostering community, sustainability, and creativity.

Specialties:
- Signature espresso blends
- Cold brews
- Artisanal teas
- Fresh-baked goods
- Plant-based and gluten-free options

Delivery Areas:
- Koregaon Park
- Viman Nagar
- Kalyani Nagar
- Camp
- Shivaji Nagar

Community Engagement:
Hosts live music nights, art showcases, and fundraisers. Uses eco-friendly packaging and supports local farmers. Free high-speed WiFi available for customers.

Working Hours:
- Monday–Friday: 7 AM – 8 PM
- Saturday: 8 AM – 8 PM
- Sunday: 8 AM – 6 PM
"""

about_us_tool = Tool(
    name="AboutUsTool",
    func=about_us_tool,
    description="Use this tool to answer questions about the coffee shop itself: story, mission, delivery areas, working hours, specialties."
)