import pandas as pd
import pytest

from src.salary_prediction import evaluate_salary_model


def sample_jobs():
    return pd.DataFrame({
        "job_id": [f"JOB-{i}" for i in range(20)], "job_title": ["Data Analyst"] * 20,
        "country": [f"country-{i}" for i in range(20)],
        "experience_level": ["Entry", "Senior"] * 10,
        "remote_option": ["Remote"] * 20, "employment_type": ["Full-time"] * 20,
        "salary_min_usd": [50000 + i * 100 for i in range(20)],
        "salary_max_usd": [60000 + i * 100 for i in range(20)],
    })


def test_experiment_supports_unseen_countries_and_keeps_test_offer_ids():
    jobs = sample_jobs()
    links = pd.DataFrame({"job_id": jobs.job_id, "skill": ["SQL"] * 20})
    scores, predictions = evaluate_salary_model(jobs, links)
    assert scores.n_train.eq(16).all()
    assert scores.n_test.eq(4).all()
    assert predictions.job_id.is_unique
    assert len(predictions) == 4
    expected = jobs.set_index("job_id").eval("(salary_min_usd + salary_max_usd) / 2")
    assert predictions.salaire_cible_usd.tolist() == expected.loc[predictions.job_id].tolist()
    assert predictions["Regression Ridge"].notna().all()
    assert predictions["Moyenne par metier"].notna().all()


def test_duplicate_job_ids_cannot_leak_across_train_and_test():
    jobs = sample_jobs()
    jobs.loc[1, "job_id"] = "JOB-0"
    links = pd.DataFrame({"job_id": ["JOB-0"], "skill": ["SQL"]})
    with pytest.raises(ValueError, match="unique"):
        evaluate_salary_model(jobs, links)


def test_title_baseline_predicts_training_mean_of_each_title():
    jobs = sample_jobs()
    jobs["job_title"] = ["Data Analyst", "Data Engineer"] * 10
    jobs["salary_max_usd"] = jobs.salary_min_usd + jobs.job_title.eq("Data Engineer") * 80000
    links = pd.DataFrame({"job_id": jobs.job_id, "skill": ["SQL"] * 20})
    _, predictions = evaluate_salary_model(jobs, links)
    titles = jobs.set_index("job_id").job_title.loc[predictions.job_id].to_numpy()
    train = jobs.loc[~jobs.job_id.isin(predictions.job_id)].assign(y=lambda d: (d.salary_min_usd + d.salary_max_usd) / 2)
    expected = pd.Series(titles).map(train.groupby("job_title").y.mean())
    assert predictions["Moyenne par metier"].to_numpy() == pytest.approx(expected.to_numpy())


def test_restricted_feature_set_matches_professor_workflow():
    jobs = sample_jobs()
    links = pd.DataFrame({"job_id": jobs.job_id, "skill": ["SQL"] * 20})
    scores, predictions = evaluate_salary_model(
        jobs,
        links,
        feature_columns=["job_title", "experience_level", "country"],
        include_skills=False,
    )
    assert {"Reference moyenne", "Moyenne par metier", "Regression Ridge"}.issubset(set(scores.index))
    assert set(predictions.columns) >= {"job_id", "salaire_cible_usd", "Reference moyenne", "Moyenne par metier", "Regression Ridge"}
    assert scores["MAE_USD"].notna().all()
