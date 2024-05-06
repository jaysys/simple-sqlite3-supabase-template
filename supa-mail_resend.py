import resend

resend.api_key = "re_eBwtvvKo_Dn6~~~hmbb"

r = resend.Emails.send({
  "from": "onboarding@resend.dev",
  "to": "jaysys@gmail.com",
  "subject": "Jaeho!!! World",
  "html": "<p>Congrats on sending your <strong>first email</strong>!</p>"
})



