import requests
from openai import OpenAI

def generate_image_from_headline(headline: str) -> bytes:
    raise Exception("API too expensive.")
    client = OpenAI()

    response = client.images.generate(
    model="dall-e-3",
    prompt=f"Make an image of this headline, photorealistic: {headline}",
    size="1024x1024",
    quality="standard",
    n=1,
    )

    image_url = response.data[0].url
    
    response = requests.get(image_url)
    return response.content

def main() -> None:
    headline = input("Enter a headline: ")
    generate_image_from_headline(headline)

if __name__ == "__main__":
    main()