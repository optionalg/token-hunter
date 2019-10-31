from logging import info, warning

from gitlab import projects, snippets, groups, issues, members, issue_comments


def process_all(args):
    personal_projects = {}
    for group in args.group:
        group_details = groups.get_group(group)
        if len(group_details) == 0:
            warning("[!] %s not found, skipping", group)
            continue

        group_projects = projects.all_group_projects(group)
        all_members = members.all_members(group)

        if args.members:
            for member in all_members:
                personal_projects.update(projects.all_member_projects(member))

        all_projects = {**group_projects, **personal_projects}

        log_group(group_details)
        log_group_projects(group_projects)
        log_members(all_members)

        if args.members:
            log_members_projects(personal_projects)

        # Go get the snippets content and log it if the switch is provided
        if args.snippets:
            info("[*] Fetching snippets for %s projects", len(all_projects))
            all_snippets = snippets.all_snippets([group_projects, personal_projects])
            all_secrets = snippets.sniff_secrets(all_snippets)
            log_related_snippets(all_snippets, [group_projects, personal_projects])
            log_snippet_secrets(all_secrets, all_snippets)

        if args.issues:
            info("[*] Fetching issues for all projects")
            all_issues = []
            all_comments = []
            all_secrets = []
            for project_id, project_url in all_projects.items():
                project_issues = issues.all_issues(project_id)
                for issue in project_issues:
                    all_issues.append(issue)
                for issue in all_issues:
                    secrets = issues.sniff_secrets({issue.web_url: issue.description})
                    for secret in secrets:
                        all_secrets.append(secret)
                for issue in project_issues:
                    comments = issue_comments.all_comments(project_id, issue.ident)
                    if len(comments) > 0:
                        all_comments.append(comments)
            log_related_issues(all_issues, all_projects)
            log_issue_secrets(all_secrets, all_issues)
            log_related_comments(all_secrets, all_comments)


def log_issue_secrets(secrets, all_issues):
    info("  FOUND (%s) SECRET(S) IN (%s) TOTAL ISSUE(S)", len(secrets), len(all_issues))
    for secret in secrets:
        info("    Url: %s Type: %s Candidate Secret: %s", secret.url, secret.secret_type, secret.secret)


def log_snippet_secrets(all_secrets, all_snippets):
    info("    FOUND (%s) SECRET(S) IN (%s) TOTAL SNIPPET(S)", len(all_secrets), len(all_snippets))
    for secret in all_secrets:
        info("      Url: %s Type: %s Candidate Secret: %s", secret.url, secret.secret_type, secret.secret)


def log_related_comments(all_issue_comments, all_issues):
    info("  COMMENTS (%s) IN ISSUES (%s)", len(all_issue_comments), len(all_issues))


def log_related_issues(all_issues, all_projects):
    info("  ISSUES (%s) IN PROJECTS (%s)", len(all_issues), len(all_projects))


def log_related_snippets(all_snippets, all_projects):
    info("  SNIPPETS (%s) IN PROJECTS (%s)", len(all_snippets), len(all_projects))


def log_group(group_details):
    info("GROUP: %s (%s)", group_details['name'], group_details['web_url'])


def log_group_projects(group_projects):
    info("  GROUP PROJECTS (%s):", len(group_projects))
    for value in group_projects.values():
        info("    %s", value)


def log_members(all_members):
    info("  MEMBERS (%s):", len(all_members))
    for member in all_members:
        info("    %s", member)


def log_members_projects(personal_projects):
    info("  MEMBERS' PERSONAL PROJECTS (%s):", len(personal_projects))
    for value in personal_projects.values():
        info("    %s", value)
