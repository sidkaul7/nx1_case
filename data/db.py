from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data.models import Result

DB_PATH = 'sqlite:///data/filings.db'
engine = create_engine(DB_PATH)
Session = sessionmaker(bind=engine)

def insert_result(id, url=None, text=None, model_output=None, validation=None, expected=None, company=None, template=None):
    session = Session()
    result = Result(
        id=id,
        url=url,
        text=text,
        model_output=model_output,
        validation=validation,
        expected=expected,
        company=company,
        template=template
    )
    session.add(result)
    session.commit()
    session.close()


def get_result_by_id(result_id):
    session = Session()
    result = session.query(Result).filter_by(id=result_id).first()
    session.close()
    return result


def get_results_by_url(url):
    session = Session()
    results = session.query(Result).filter_by(url=url).all()
    session.close()
    return results

def result_to_dict(result):
    if not result:
        return None
    return {
        'id': result.id,
        'url': result.url,
        'text': result.text,
        'model_output': result.model_output,
        'validation': result.validation,
        'expected': result.expected,
        'company': result.company,
        'template': result.template
    } 