import pytest
import json
from app import app
from model import Session, News

@pytest.fixture
def client():
    """Configure test client for Flask application"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_news_data():
    """Example data for news test"""

    data = {
        "title": "Thousands of ‘No Kings’ protesters gather at Portland’s Waterfront Park",
        "text": "PORTLAND Ore. (KPTV) - Oregonians flooded the Portland waterfront on Saturday for the third round of “No Kings” protests. “We have to stand up,” protester Sarah Gomm said. “We have to show at least our representatives what we want because they are not serving us right now.” From immigration to foreign policy, protesters made their frustrations with President Donald Trump clear. “There’s a lot of reasons for us to be here together and especially as a clergyperson who leans into what it means to care and love our neighbor, what’s happening right now is the anathema of kindness and caring for our neighbor,” local deacon Sue Best said. Organizers estimate tens of thousands of people showed up to the waterfront, shutting down roads as they marched through the city. Portland was not alone — dozens of protests took place across the state. In Gresham, the rally drew a large crowd and a couple of counterprotesters. “I’m out here because I happen to believe that Donald Trump is the best president that we could have for this country right now,” Kamala Pati said. The White House also chimed in. Spokesperson Abigail Jackson said, “The only people who care about these Trump Derangement Therapy Sessions are the reporters who are paid to cover them.” Protesters pushed back on the statement. “We’re all here because we care about our country,” Best said. “We care about our constitution, and we care about each other and our communities and we want for us in this country and our world stage to be seen as people who have a kindness and not cruelty at the center of our democracy.” The protests come three days after the Ninth U.S. Circuit Court of Appeals paused a federal order limiting the use of tear gas and other chemical munitions at the Portland ICE facility. No Kings organizers said they are committed to nonviolent action and expect protesters to help deescalate any potential conflict. The Portland Police Bureau has dedicated teams on the ground to keep things safe and running smoothly. “We want everyone to feel safe and be able to peacefully express their First Amendment Rights,” a spokesperson said. The rally is part of a larger national protest against the Trump administration.",
    }

    yield data

    # Clean the news of the database after each test
    session = Session()
    existing_news = session.query(News).filter(News.title == data['title']).first()
    if existing_news:
        session.delete(existing_news)
        session.commit()
    session.close()

def test_home_redirect(client):
    """Tests if the home route redirects to the frontend"""
    response = client.get('/')
    assert response.status_code == 302
    assert '/front/index.html' in response.location

def test_docs_redirect(client):
    """Test if the docs route redirects to openapi"""
    response = client.get('/docs')
    assert response.status_code == 302
    assert '/openapi' in response.location

def test_get_news_empty(client):
    """Test the news listing when there are none"""
    response = client.get('/news')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'news' in data
    assert isinstance(data['news'], list)

def test_add_news_prediction(client, sample_news_data):
    """Test adding a news with prediction"""

    # Adds news to the database
    response = client.post('/news', data=sample_news_data)
    assert response.status_code == 200
    data = json.loads(response.data)

    # Checks if the news was properly created
    assert data['title'] == sample_news_data['title']
    assert data['text'] == sample_news_data['text']

    # Checks if the prediction was done correctly (label field must be present)
    assert 'label' in data
    assert data['label'] in [0, 1]

def test_add_duplicate_news(client, sample_news_data):
    """Test adding a duplicate news"""

    # First of all, adds the news
    client.post('/news', data=sample_news_data)
    
    # Then, tries to add again
    response = client.post('/news', data=sample_news_data)
    
    assert response.status_code == 409
    data = json.loads(response.data)
    assert 'message' in data
    assert 'already exists' in data['message']

def test_add_invalid_news(client, sample_news_data):
    """Tests adding a news with invalid fields"""

    # Creates a news item with empty fields
    news = { "title": "", "text": "" }
    
    response = client.post('/news', data=news)
    
    assert response.status_code == 422
    data = json.loads(response.data)
    assert 'message' in data
    assert 'field is required' in data['message']

    # Creates a news item with a short length text field
    news = { "title": "Teste", "text": "Teste" }
    
    response = client.post('/news', data=news)
    
    assert response.status_code == 422
    data = json.loads(response.data)
    assert 'message' in data
    assert 'must be at least 300 characters long' in data['message']

def test_delete_news(client, sample_news_data):
    """Tests news deletion"""

    # Adds the news
    response = client.post('/news', data=sample_news_data)
    data = json.loads(response.data)

    # Delete it
    response = client.delete(f'/news/{data["id"]}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    assert 'removed successfully' in data['message']

def test_delete_nonexistent_news(client):
    """Tests the deletion of a non existing news"""
    response = client.delete('/news/999999999999999')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'message' in data