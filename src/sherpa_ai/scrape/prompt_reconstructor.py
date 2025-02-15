import sherpa_ai.config as cfg
from sherpa_ai.scrape.extract_github_readme import extract_github_readme
from sherpa_ai.utils import (
    chunk_and_summarize,
    count_string_tokens,
    get_link_from_slack_client_conversation,
    rewrite_link_references,
    scrape_with_url,
)


class PromptReconstructor:
    def __init__(self, question, slack_message):
        self.question = question
        self.slack_message = slack_message

    def reconstruct_prompt(self, user_id=None, team_id=None):
        question = self.question
        last_message = self.slack_message
        last_message_links = get_link_from_slack_client_conversation(last_message)

        # if there is a link inside the question scrape then summarize based
        # on question and then aggregate to the question

        if len(last_message_links) > 0:
            available_token = 3000 - count_string_tokens(question, "gpt-3.5-turbo")
            per_scrape_token_size = available_token / len(last_message_links)
            final_summary = []
            for last_message_link in last_message_links:
                link = last_message_link["url"]
                scraped_data = ""
                if "github" in last_message_links[-1]["base_url"]:
                    git_scraper = extract_github_readme(link)
                    if git_scraper:
                        scraped_data = {
                            "data": extract_github_readme(link),
                            "status": 200,
                        }
                    else:
                        scraped_data = {"data": "", "status": 404}
                else:
                    scraped_data = scrape_with_url(link)
                if scraped_data["status"] == 200:
                    chunk_summary = chunk_and_summarize(
                        link=link,
                     
                        question=question,
                        text_data=scraped_data["data"],
                        user_id=user_id,
                        team_id=team_id,
                    )

                    while (
                        count_string_tokens(chunk_summary, "gpt-3.5-turbo")
                        > per_scrape_token_size
                    ):
                        chunk_summary = chunk_and_summarize(
                            link=link,
                            question=question,
                            text_data=chunk_summary,
                            user_id=user_id,
                            team_id=team_id,
                        )

                    final_summary.append({"data": chunk_summary, "link": link})

            question = rewrite_link_references(question=question, data=final_summary)
        return question
