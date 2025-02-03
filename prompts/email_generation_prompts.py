github_prompt = """
            Generate and design 25 professional mock emails about GitHub pull request notifications.
            Write the emails imitating if the pull requests have been notified for review to the person with first name of Tevfik Emre and surname Sungur. Inform the person in the email.
            Include fields such as commit id, subject, comiiter, description, date and hour.
            These notification emails will be generated based on one specific repository: tgstation/tgstation.
            If the total obtained pull request count from the repository is less than 25, then generate that amount of emails.
            I need you to generate these emails with the given objective:
                1 - Pull request notification email, including details about the pull request commit.
                2 - Summarize the pull request message, if necessary.
                3 - Display the pull request date with day and hour seperately.
            Return the emails in a finalized list, as each element will include email objects with fields 'subject' and 'body' and 'category' which is 'Github PR' for all emails.
            The 'body' field should include all other fields as well, which are 'subject' and 'category'.
            Finally, store the final mail list in local files, both in plain text and vector.
            Print how many emails have been stored at the end.
    """

security_prompt = """
            Generate and design professional mock emails as much as possible imitating if there is a security warning in the person's possible softwares and devices.
            Write the emails to the person with first name of Tevfik Emre and surname Sungur.
            These notification emails will be generated based on realistic security warning cases. The realistic cases will be fetched from: https://blog.admindroid.com/top-15-vulnerabilities-in-microsoft-365/
            Do not leave any mails hypothetical and fill each email with fetched security issues creatively.
            I need you to generate these emails with the given objective:
                1 - Include details about the warning.
                2 - Display the security warning date with day and hour seperately.
            Return the emails in a finalized list, as each element will include email objects with fields 'subject' and 'body' and 'category' which is 'Security' for all emails.
            Finally, store the final mail list in local files, both in plain text and vector.
            Print how many emails have been stored at the end.
    """

billing_prompt = """
            Generate and design multiple, ideally 15, billing notification emails for the customer, as if a product has been purchased by the corresponding person.
            Write the emails to the person with first name of Tevfik Emre and surname Sungur.
            These notification emails will be generated based on real products in each email generation.
            Do not leave any mails hypothetical and fill each email with distinct real product information.
            I need you to generate these emails with the given objective:
                1 - Inform the person about the awaiting purchase first and let the person know that he/she needs to pay in the future.
                2 - Include details about the product that has been purchased (product name, price, description, link).
            Return the emails in a finalized list, as each element will include email objects with fields 'subject' and 'body' and 'category' which is 'Billing' for all emails.
            Finally, store the final mail list in local files, both in plain text and vector.
            Print how many emails have been stored at the end.
    """