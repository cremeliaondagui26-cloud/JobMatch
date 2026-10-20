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


def test_salary_or_identifier_cannot_be_used_as_a_feature():
    jobs = sample_jobs()
    for column in ["salary_min_usd", "salary_max_usd", "salary_midpoint_usd", "job_id"]:
        with pytest.raises(ValueError, match="Variables explicatives"):
            evaluate_salary_model(jobs, feature_columns=["job_title", column], include_skills=False)


def test_nonfinite_and_reversed_salaries_are_excluded():
    jobs = sample_jobs()
    jobs["salary_min_usd"] = jobs.salary_min_usd.astype(float)
    jobs.loc[0, "salary_min_usd"] = float("inf")
    jobs.loc[1, "salary_min_usd"] = 1000000
    scores, predictions, split = evaluate_salary_model(jobs, include_skills=False, return_split=True)
    assert split["excluded_salary_rows"] == 2
    assert not set(["JOB-0", "JOB-1"]) & (set(split["X_train"].index) | set(predictions.job_id))
    assert scores.MAE_USD.notna().all()


def test_test_only_skills_are_not_in_training_vocabulary():
    from sklearn.model_selection import train_test_split
    jobs = sample_jobs()
    _, test_ids = train_test_split(jobs.job_id.to_numpy(), test_size=0.2, random_state=42)
    links = pd.DataFrame({"job_id": jobs.job_id, "skill": ["SQL"] * len(jobs)})
    links = pd.concat([links, pd.DataFrame({"job_id": [test_ids[0]], "skill": ["TestOnly"]})], ignore_index=True)
    _, _, split = evaluate_salary_model(jobs, links, return_split=True)
    assert "skill::SQL" in split["X_train"].columns
    assert "skill::TestOnly" not in split["X_train"].columns


def test_unseen_job_title_uses_training_global_mean_for_title_baseline():
    from sklearn.model_selection import train_test_split
    jobs = sample_jobs()
    _, test_ids = train_test_split(jobs.job_id.to_numpy(), test_size=0.2, random_state=42)
    jobs.loc[jobs.job_id.eq(test_ids[0]), "job_title"] = "Unseen title"
    _, predictions, split = evaluate_salary_model(jobs, include_skills=False, return_split=True)
    prediction = predictions.loc[predictions.job_id.eq(test_ids[0]), "Moyenne par metier"].item()
    assert prediction == pytest.approx(split["y_train"].mean())
