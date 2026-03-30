import pytest
import json
from app import app
from model import Session, News

@pytest.fixture
def client():
    """Configura o cliente de teste para a aplicação Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_news_data():
    """Dados de exemplo para teste de notícia"""

    data = {
        "title": "Thousands of ‘No Kings’ protesters gather at Portland’s Waterfront Park",
        "text": "PORTLAND Ore. (KPTV) - Oregonians flooded the Portland waterfront on Saturday for the third round of “No Kings” protests. “We have to stand up,” protester Sarah Gomm said. “We have to show at least our representatives what we want because they are not serving us right now.” From immigration to foreign policy, protesters made their frustrations with President Donald Trump clear. “There’s a lot of reasons for us to be here together and especially as a clergyperson who leans into what it means to care and love our neighbor, what’s happening right now is the anathema of kindness and caring for our neighbor,” local deacon Sue Best said. Organizers estimate tens of thousands of people showed up to the waterfront, shutting down roads as they marched through the city. Portland was not alone — dozens of protests took place across the state. In Gresham, the rally drew a large crowd and a couple of counterprotesters. “I’m out here because I happen to believe that Donald Trump is the best president that we could have for this country right now,” Kamala Pati said. The White House also chimed in. Spokesperson Abigail Jackson said, “The only people who care about these Trump Derangement Therapy Sessions are the reporters who are paid to cover them.” Protesters pushed back on the statement. “We’re all here because we care about our country,” Best said. “We care about our constitution, and we care about each other and our communities and we want for us in this country and our world stage to be seen as people who have a kindness and not cruelty at the center of our democracy.” The protests come three days after the Ninth U.S. Circuit Court of Appeals paused a federal order limiting the use of tear gas and other chemical munitions at the Portland ICE facility. No Kings organizers said they are committed to nonviolent action and expect protesters to help deescalate any potential conflict. The Portland Police Bureau has dedicated teams on the ground to keep things safe and running smoothly. “We want everyone to feel safe and be able to peacefully express their First Amendment Rights,” a spokesperson said. The rally is part of a larger national protest against the Trump administration.",
    }

    yield data

    # Primeiro, limpa qualquer notícia existente com o mesmo nome
    session = Session()
    existing_news = session.query(News).filter(News.title == data['title']).first()
    if existing_news:
        session.delete(existing_news)
        session.commit()
    session.close()

def test_home_redirect(client):
    """Testa se a rota home redireciona para o frontend"""
    response = client.get('/')
    assert response.status_code == 302
    assert '/front/index.html' in response.location

# def test_docs_redirect(client):
#     """Testa se a rota docs redireciona para openapi"""
#     response = client.get('/docs')
#     assert response.status_code == 302
#     assert '/openapi' in response.location

def test_get_news_empty(client):
    """Testa a listagem de notícias quando não há nenhuma"""
    response = client.get('/news')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'news' in data
    assert isinstance(data['news'], list)

def test_add_news_prediction(client, sample_news_data):
    """Testa a adição de uma notícia com predição"""

    # Teste de adição
    response = client.post('/news', data=sample_news_data)
    
    assert response.status_code == 200
    data = json.loads(response.data)

    # Verifica se o notícia foi criado com todas as informações
    assert data['title'] == sample_news_data['title']
    assert data['text'] == sample_news_data['text']

    # Verifica se a predição foi feita (label deve estar presente)
    assert 'label' in data
    assert data['label'] in [0, 1]

def test_add_duplicate_news(client, sample_news_data):
    """Testa a adição de uma notícia duplicadoa"""

    # Primeiro adiciona a notícia
    client.post('/news', data=sample_news_data)
    
    # Tenta adicionar novamente
    response = client.post('/news', data=sample_news_data)
    
    assert response.status_code == 409
    data = json.loads(response.data)
    assert 'message' in data
    assert 'already exists' in data['message']

def test_add_invalid_news(client, sample_news_data):
    """Testa a adição de uma notícia com campos inválidos"""

    # Cria notícia com campos vazios
    news = { "text": "", "title": "" }
    
    response = client.post('/news', data=news)
    
    assert response.status_code == 422
    data = json.loads(response.data)
    assert 'message' in data
    assert 'field is required' in data['message']

    # Cria notícia com texto de tamanho insuficiente
    news = { "text": "Teste", "title": "Teste" }
    
    response = client.post('/news', data=news)
    
    assert response.status_code == 422
    data = json.loads(response.data)
    assert 'message' in data
    assert 'must be at least 300 characters long' in data['message']

def test_delete_news(client, sample_news_data):
    """Testa a remoção de um ´notícia"""


    # Adiciona o notícia
    response = client.post('/news', data=sample_news_data)
    data = json.loads(response.data)

    # Remove a notícia
    response = client.delete(f'/news/{data["id"]}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    assert 'removed successfully' in data['message']

def test_delete_nonexistent_news(client):
    """Testa a remoção de uma notícia que não existe"""
    response = client.delete('/news/999999999999999')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'message' in data

def cleanup_test_news():
    """Limpa notícia de teste do banco"""

    session = Session()
    test_news = session.query(News).filter(News.title.like("%No Kings%")).all()

    for news in test_news:
        session.delete(news)
    session.commit()
    session.close()

# Executa limpeza após os testes
def test_cleanup():
    """Limpa dados de teste"""
    cleanup_test_news()