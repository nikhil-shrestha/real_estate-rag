from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.config import config
import logging

logger = logging.getLogger(__name__)

# Initialize LLM
llm = ChatOpenAI(
    model_name=config.OPENAI_MODEL, 
    temperature=config.LLM_TEMPERATURE,
    api_key=config.OPENAI_API_KEY
)
parser = StrOutputParser()

# Enhanced prompts with better instructions
expand_prompt = PromptTemplate.from_template("""
You are a real estate assistant. Your task is to clarify and expand the following real estate inquiry to make it more specific and searchable.

Original inquiry: "{message}"

Please provide a clearer, more detailed version of this inquiry that would help in finding relevant property information. Focus on:
- Property type and features
- Location preferences
- Budget considerations
- Specific needs or requirements

Expanded inquiry:
""")

category_prompt = PromptTemplate.from_template("""
Classify the following real estate inquiry into exactly one of these categories:
- Price Inquiry
- Availability Check
- Schedule Visit
- Neighborhood Info
- Financing Question
- General Inquiry

Inquiry: "{message}"

Consider the main intent of the inquiry. Respond with only the category name.

Category:
""")

# Enhanced category-specific prompts
category_prompts = {
    "Price Inquiry": PromptTemplate.from_template("""
You are a helpful real estate assistant specializing in pricing information.

Context from property database:
{context}

Customer inquiry: {question}

Please provide a comprehensive response about pricing, including:
- Current market prices for similar properties
- Price ranges and factors affecting pricing
- Payment options and financing considerations
- Value propositions

Response:
"""),
    
    "Availability Check": PromptTemplate.from_template("""
You are a helpful real estate assistant specializing in property availability.

Context from property database:
{context}

Customer inquiry: {question}

Please provide information about:
- Current availability status
- Timeline for availability
- Similar available properties
- Next steps for interested buyers

Response:
"""),
    
    "Schedule Visit": PromptTemplate.from_template("""
You are a helpful real estate assistant specializing in property viewings.

Context from property database:
{context}

Customer inquiry: {question}

Please provide information about:
- How to schedule a viewing
- What to expect during the visit
- Best times for viewings
- Preparation recommendations

Response:
"""),
    
    "Neighborhood Info": PromptTemplate.from_template("""
You are a helpful real estate assistant specializing in neighborhood information.

Context from property database:
{context}

Customer inquiry: {question}

Please provide comprehensive neighborhood information including:
- Local amenities and facilities
- Transportation options
- Safety and community features
- Lifestyle and demographics

Response:
"""),
    
    "Financing Question": PromptTemplate.from_template("""
You are a helpful real estate assistant specializing in financing options.

Context from property database:
{context}

Customer inquiry: {question}

Please provide information about:
- Financing options available
- Loan requirements and processes
- Down payment considerations
- Monthly payment estimates

Response:
"""),
    
    "General Inquiry": PromptTemplate.from_template("""
You are a helpful real estate assistant providing general information.

Context from property database:
{context}

Customer inquiry: {question}

Please provide a comprehensive and helpful response based on the available information.

Response:
""")
}

# Create chains
expand_chain = expand_prompt | llm | parser
category_chain = category_prompt | llm | parser