from langchain.tools import Tool
from Backend.Tools.detailsagents_tools.retriever_tool import vectorstore
from Backend.schemas.detailsagent_tools_schemas import ProductPriceInfo, ProductPriceListOutput , PriceCheckInput

def get_price_func(product_names: PriceCheckInput) -> ProductPriceListOutput:
    product_info_list = []

    for item in product_names:
        name = item.name
        is_available = item.is_available

        if is_available:
            name_normalized = name.strip().title()

            results = vectorstore.similarity_search(
                query="",
                k=1,
                filter={"name": {"$eq": name_normalized}}
            )

            if results:
                doc = results[0]
                price = doc.metadata.get("price", 0.0)
                product_info_list.append(
                    ProductPriceInfo(
                        name=doc.metadata["name"],
                        is_available=True,
                        price=price
                    )
                )
            else:
                product_info_list.append(
                    ProductPriceInfo(
                        name=name,
                        is_available=True,
                        price=0.0
                    )
                )
        else:
            product_info_list.append(
                ProductPriceInfo(
                    name=name,
                    is_available=False,
                    price=0.0
                )
            )

    return ProductPriceListOutput(products=product_info_list)

get_price_tool = Tool.from_function(
    name="GetPriceTool",
    func=get_price_func,
    description="""
            Get the price of one or more products. 

            ⚠️ Only use this tool if:
            - The product has already been verified as available using the CheckAvailabilityTool.
            - Do NOT call this tool directly if availability is unknown.
            If availability hasn’t been checked, call CheckAvailabilityTool first.
            """,
    args_schema=PriceCheckInput
)
