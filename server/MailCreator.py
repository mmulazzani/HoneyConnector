import random

# so... what you are now looking at are the remains of a improved mail module I had in mind during development, when I
# thought I would transfer contents of e-mails from the IMAP server to the client
# this idea was abandoned after checking the behaviour of Thunderbird and because of time constraints

# the reason for this class was to populate mailboxes with random e-mails of certain categories with certain possibilities.
# not used at the moment, but maybe one day down the line this might be useful, so I still included this

def getWeightedRandom(setList):
    maxOccurance = sum(setList)
    randomSeed = random.randrange(1, maxOccurance)
    currentSeedTest = 0
    result = 0
    for i in xrange(len(setList)):
        currentSeedTest = currentSeedTest + setList[i]
        if randomSeed <= currentSeedTest:
            result = i + 1
            break
    return result

def retrieveTemplate(type, language):
    pass

def getLanguage():
    langs = ['en', 'de']
    return random.choice(langs)
    
def createSpamMail(address, name):
    #1 = nonsens, 2 = products, 3 = phishing, 4 = newsletter
    spamType = random.randrange(1,4)
    lang = getLanguage()
    if spamType == 1:
        return "nonsens " + lang
    elif spamType == 2:
        # 1 = forgery, 2 = insurance, 3 = viagra, 4 = credits, 5 = pr0n, 6 = gambling, 7 = vacation, 8 = jobs
        productType = random.randrange(1,8)
        if productType == 1:
            return "forgery " + lang
        elif productType == 2:
            return "insurance " + lang
        elif productType == 3:
            return "viagra " + lang
        elif productType == 4:
            return "credits " + lang
        elif productType == 5:
            return "pr0n " + lang
        elif productType == 6:
            return "gambling " + lang
        elif productType == 7:
            return "vacation " + lang
        elif productType == 8:
            return "jobs " + lang
    elif spamType == 3:
        # 1 = nigerian prince, 2 = banking, 3 = hosting, 4 = facebook, 5 = packstation
        phishType = random.randrange(1,5)
        if phishType == 1:
            return "nigerian prince " + lang
        elif phishType == 2:
            return "banking " + lang
        elif phishType == 3:
            return "hosting " + lang
        elif phishType == 4:
            return "facebook " + lang
        elif phishType == 5:
            return "packstation " + lang
    elif spamType == 4:
        return "newsletter " + lang    
    
def getMobile():
    # 1 = not mobile, 2 = iphone, 3 = ipad, 4 = android
    probSet = [50,20,10,30]
    mobileType = getWeightedRandom(probSet)
    if mobileType == 1:
        return "not mobile"
    elif mobileType == 2:
        return "iphone"
    elif mobileType == 3:
        return "ipad"
    elif mobileType == 4:
        return "android"
    
def getReplyType():
    # 1 = no reply, 2 = reply
    probSet = [75, 25]
    isReply = getWeightedRandom(probSet)
    if isReply == 1:
        return False
    elif isReply == 2:
        return True
    
def getMailCase():
    # 1 = normal, 2 = lowerscore, 3 = ALL CAPS
    probSet = [40, 55, 5]
    isCase = getWeightedRandom(probSet)
    if isCase == 1:
        return "norm"
    elif isCase == 2:
        return "lower"
    elif isCase == 3:
        return "caps"
    

def createPrivateMail(address, name):
    # 1 = funny mail, 2 = appointment, 3 = useless conversation
    privateType = random.randrange(1,3)
    mobileSig = getMobile()
    isReply = getReplyType()
    mailCase = getMailCase()
    if privateType == 1:
        return "funny mail " + mobileSig
    elif privateType == 2:
        return "appointment " + mobileSig
    elif privateType == 3:
        return "useless conversation " + mobileSig


def createOrderMail(address, name):
    return "orders"    

def createAccountMail(address, name):
    return "account"    


def createMail(address, name):
    # 1 = spam, 2 = private, 3 = orders, 4 = account data
    probSet = [75, 20, 3, 2]
    mailType = getWeightedRandom(probSet)
    if mailType == 1:
        mail = createSpamMail(address, name)
    elif mailType == 2:
        mail = createPrivateMail(address, name)
    elif mailType == 3:
        mail = createOrderMail(address, name)
    elif mailType == 4:
        mail = createAccountMail(address, name)
    return mail

def createMailSet(address, name):
    count = random.randrange(1, 500)
    for i in xrange(count - 1):
        print createMail(address, name)
    
createMailSet("asdf0", "asdasd")
