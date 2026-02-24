from langchain_core.tools import Tool
import logging

logger = logging.getLogger(__name__)


def about_us_func(_: str = "") -> str:
    """
    Provides information about Merry's Way Coffee including 
    mission, story, specialties, and delivery zones.
    
    Args:
        _: Unused parameter for compatibility
    
    Returns:
        str: Comprehensive shop information
    """
    try:
        shop_info = """**Merry's Way Coffee** - Koregaon Park, Pune

**Our Story:**
Founded in 2015 as a family-owned café with a mission to share quality, ethically-sourced coffee with our community. Our founder's journey through South America led to partnerships with small farms and cooperatives. We roast beans in-house to bring out regional flavors.

**Mission:**
Provide quality, ethically-sourced coffee while fostering community, sustainability, and creativity.

**Specialties:**
• Signature espresso blends
• Cold brews & artisanal teas
• Fresh-baked goods daily
• Plant-based & gluten-free options

**Hours:**
• Monday–Friday: 7 AM – 8 PM
• Saturday: 8 AM – 8 PM
• Sunday: 8 AM – 6 PM

**Delivery Areas:**
Koregaon Park • Viman Nagar • Kalyani Nagar • Camp • Shivaji Nagar

**Community:**
We host live music nights, art showcases, and fundraisers. Eco-friendly packaging, support for local farmers, and free high-speed WiFi for all customers.
"""
        logger.info("Shop information requested")
        return shop_info
        
    except Exception as e:
        logger.error(f"Error retrieving shop information: {str(e)}")
        return f"Sorry, I couldn't retrieve shop information right now. Error: {str(e)}"


# Create tool
about_us_tool = Tool(
    name="AboutUsTool",
    func=about_us_func,
    description=(
        "Get information about the coffee shop: story, mission, hours, "
        "location, delivery areas, and specialties. No input required."
    )
)
