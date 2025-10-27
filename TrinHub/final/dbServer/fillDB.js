async function fillDB() {
  const firstNames = [ "Madhavendra", "Emily", "Michael", "Sophia", "William", "Olivia", "Ethan", "Nicholas", "Daniel", "Isabella", "Matthew", "Ava", "Jacob", "Mia", "Christopher", "Abigail", "Joshua", "Charlotte", "Andrew", "Madison", "Joseph", "Harper", "Samuel", "Evelyn", "James", "Elizabeth", "Benjamin", "Avery", "David", "Lily", "Gabriel", "Sofia", "John", "Grace", "Jonathan", "Chloe", "Nathan", "Zoey", "Samuel", "Victoria", "Ryan", "Hannah", "Nicholas", "Natalie", "Caleb", "Audrey", "Isaac", "Leah", "Dylan", "Stella", "Jackson", "Maya", "Luke", "Penelope", "Christian", "Anna", "Wyatt", "Ariana", "Owen", "Ruby", "Julian", "Claire", "Hunter", "Sadie", "Eli", "Layla", "Aaron", "Eleanor", "Charles", "Aria", "Lincoln", "Paisley", "Isaac", "Gabriella", "Zachary", "Skylar", "Anthony", "Autumn", "Cameron", "Caroline", "Colton", "Trinity", "Thomas", "Eliana", "Gavin", "Naomi", "Dominic", "Sophie", "Levi", "Addison", "Henry", "Elena", "Sebastian", "Lillian", "Christopher", "Kaylee", "Brandon", "Isla", "Adam", "Audrey"];
  const lastNames = [ "Thakur", "Johnson", "Brown", "Williams", "Jones", "Garcia", "Iofin", "Hutfilz", "Rodriguez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Taylor", "Thomas", "Moore", "Jackson", "White", "Harris", "Martin", "Thompson", "Lee", "Martinez", "Clark", "Lewis", "Hall", "Walker", "Perez", "Hall", "Young", "Scott", "King", "Hill", "Green", "Baker", "Adams", "Nelson", "Wright", "Carter", "Turner", "Allen", "Baker", "Cook", "Parker", "Rivera", "Wood", "Roberts", "Evans", "Phillips", "Ross", "Mitchell", "Hall", "Ward", "Ramirez", "Price", "Watson", "Reed", "Sanders", "Nelson", "Murphy", "Ross", "Morgan", "Stewart", "Turner", "Barnes", "Butler", "Powell", "Coleman", "Henderson", "Sullivan", "Perry", "Bailey", "Simmons", "Cox", "Howard", "Long", "Reed", "Hughes", "Foster", "Morris", "Richardson", "Price", "Ward", "Bennett", "Collins", "Murphy", "Hill", "Russell", "Diaz", "Griffin", "Cooper", "Torres", "Iofin", "Gohde", "Vinnakota", "Rose", "Striker", "Gwara", "Williamson"];
  const nouns = [ "apple", "book", "car", "dog", "tree", "house", "computer", "chair", "ocean", "flower", "bird", "mountain", "sun", "moon", "river", "cloud", "pen", "phone", "table", "door", "cat", "road", "guitar", "sky", "ball", "cake", "clock", "desk", "mirror", "window", "lamp", "key", "globe", "bike", "hat", "shoe", "cookie", "painting", "camera", "map", "chair", "bed", "shirt", "sock", "cup", "plate", "spoon", "fork", "knife", "napkin", "couch", "pillow", "blanket", "towel", "television", "radio", "microphone", "glasses", "bottle", "oven", "refrigerator", "toaster", "microwave", "wallet", "purse", "belt", "watch", "ring", "necklace", "earrings", "bracelet", "socks", "underwear", "pants", "shorts", "dress", "skirt", "jacket", "coat", "scarf", "gloves", "boots", "sneakers", "sandals", "high heels", "tie", "suit", "uniform", "badge", "flag", "banner", "trophy", "medal", "award", "ribbon", "boat", "scooter", "boot", "laptop", "pencil"];
  const adjectives = ["Ambitious" ,"Brave" ,"Caring" ,"Determined" ,"Energetic" ,"Friendly" ,"Generous" ,"Honest" ,"Intelligent" ,"Kind" ,"Loyal" ,"Modest" ,"Optimistic" ,"Passionate" ,"Reliable" ,"Strong" ,"Talented" ,"Unique" ,"Wise" ,"Adventurous" ,"Bold" ,"Cheerful" ,"Diligent" ,"Empathetic" ,"Gracious" ,"Humble" ,"Inventive" ,"Joyful" ,"Logical" ,"Nurturing" ,"Open-minded" ,"Patient" ,"Respectful" ,"Sincere" ,"Thoughtful" ,"Versatile" ,"Analytical" ,"Bright" ,"Creative" ,"Disciplined" ,"Enthusiastic" ,"Forgiving" ,"Grateful" ,"Imaginative" ,"Jovial" ,"Knowledgeable" ,"Motivated" ,"Optimistic" ,"Perceptive" ,"Reflective" ,"Selfless" ,"Trustworthy" ,"Vibrant" ,"Witty" ,"Ambivalent" ,"Blissful" ,"Charming" ,"Daring" ,"Elegant" ,"Fearless" ,"Graceful" ,"Helpful" ,"Incisive" ,"Jolly" ,"Kind-hearted" ,"Magnificent" ,"Noble" ,"Outgoing" ,"Playful" ,"Radiant" ,"Serene" ,"Tactful" ,"Vivacious" ,"Youthful" ,"Zestful" ,"Alluring" ,"Captivating" ,"Delightful" ,"Exuberant" ,"Fascinating" ,"Glorious" ,"Harmonious" ,"Inspiring" ,"Joyous" ,"Kindly" ,"Merciful" ,"Noble-minded" ,"Open-hearted" ,"Polite" ,"Radiant" ,"Spirited" ,"Tender-hearted" ,"Warm-hearted" ,"Zealous" ,"Affectionate" ,"Compassionate" ,"Dedicated" ,"Gentle" ,"Honest" ,"Respectable"]
  const links = [ "https://www.nasa.gov/", "https://www.nationalgeographic.com/science/", "https://www.popsci.com/", "https://www.khanacademy.org/", "https://www.coursera.org/", "https://www.edx.org/", "https://www.nytimes.com/", "https://www.bbc.com/news", "https://www.cnn.com/", "https://www.mayoclinic.org/", "https://www.webmd.com/", "https://www.cdc.gov/", "https://github.com/", "https://stackoverflow.com/", "https://www.codecademy.com/", "https://www.imdb.com/", "https://www.spotify.com/", "https://www.youtube.com/", "https://www.bloomberg.com/", "https://www.investopedia.com/", "https://www.wsj.com/",  "https://www.tripadvisor.com/", "https://www.nationalgeographic.com/travel/", "https://www.airbnb.com/", "https://www.economist.com/", "https://www.nationalgeographic.com/", "https://www.scientificamerican.com/", "https://www.nature.com/", "https://www.sciencedaily.com/", "https://www.space.com/", "https://www.wired.com/", "https://www.theverge.com/", "https://www.techradar.com/", "https://www.theguardian.com/us/technology", "https://www.newscientist.com/", "https://www.sciencenews.org/", "https://www.quantamagazine.org/", "https://www.britannica.com/", "https://www.dictionary.com/", "https://www.thesaurus.com/", "https://www.poetryfoundation.org/", "https://www.history.com/", "https://www.biography.com/", "https://www.loc.gov/", "https://www.smithsonianmag.com/", "https://www.archaeology.org/", "https://www.psychologytoday.com/", "https://www.medicalnewstoday.com/", "https://www.medicinenet.com/", "https://www.cancer.org/", "https://www.diabetes.org/", "https://www.alz.org/", "https://www.webmd.com/diabetes/default.htm", "https://www.diabetes.co.uk/", "https://www.diabetes.org.uk/", "https://www.diabetes.org.uk/information/diabetes-the-basics/what-is-diabetes", "https://www.ncbi.nlm.nih.gov/pubmed/", "https://www.healthline.com/", "https://www.worldometers.info/", "https://www.who.int/", "https://www.un.org/", "https://www.europa.eu/", "https://www.fda.gov/", "https://www.cia.gov/library/publications/resources/the-world-factbook/", "https://www.census.gov/", "https://www.data.gov/", "https://www.usa.gov/", "https://www.eia.gov/", "https://www.energy.gov/", "https://www.epa.gov/", "https://www.weather.gov/", "https://www.noaa.gov/", "https://www.usgs.gov/", "https://www.fema.gov/", "https://www.nist.gov/", "https://www.nasa.gov/audience/forstudents/index.html", "https://www.nasa.gov/audience/forstudents/5-8/features/nasa-knows/what-is-nasa-288.html", "https://www.nasa.gov/kidsclub/index.html", "https://www.nasa.gov/kidsclub/flash/index.html", "https://www.nasa.gov/centers/kennedy/about/information/didyouknow.html", "https://www.nasa.gov/externalflash/m2k4/launch/index.html", "https://www.nasa.gov/audience/forstudents/k-4/index.html", "https://www.nasa.gov/mission_pages/shuttle/launch/index.html", "https://www.nasa.gov/externalflash/m2k4/landing/index.html", "https://www.nasa.gov/externalflash/ISSRG/pip_popup/index.html", "https://www.nasa.gov/mission_pages/station/structure/elements/index.html", "https://www.nasa.gov/mission_pages/station/overview/index.html", "https://www.nasa.gov/mission_pages/hubble/main/index.html", "https://www.nasa.gov/mission_pages/apollo/index.html", "https://www.nasa.gov/mission_pages/mer/news/mer20040609.html", "https://www.nasa.gov/mission_pages/phoenix/main/index.html", "https://www.nasa.gov/mission_pages/kepler/main/index.html", "https://www.nasa.gov/mission_pages/galex/index.html", "https://www.nasa.gov/mission_pages/GLAST/main/index.html", "https://www.nasa.gov/mission_pages/noaa-n/index.html", "https://www.nasa.gov/mission_pages/newhorizons/main/index.html", "https://www.nasa.gov/mission_pages/stereo/main/index.html", "https://www.nasa.gov/mission_pages/tdm/", "https://www.nasa.gov/mission_pages/grail/main/index.html", "https://www.nasa.gov/mission_pages/sdo/main/index.html"];
  const competitions = [ "Chess Championship", "Math Olympiad", "Science Fair", "Debate Tournament", "Coding Hackathon", "Art Exhibition", "Robotics Competition", "Spelling Bee", "Basketball Tournament", "Soccer League", "Crossword Puzzle Contest", "Music Competition", "Cooking Challenge", "Poetry Slam", "Film Festival", "Dance Competition", "Physics Bowl", "Quiz Bowl", "E-sports Tournament", "Chess Blitz", "Hackathon", "Mathematics Competition", "Science Olympiad", "Debate Championship", "Art Contest", "Robotics Challenge", "Spelling Contest", "Basketball Championship", "Soccer Tournament", "Crossword Puzzle Challenge", "Music Festival", "Cooking Competition", "Poetry Reading", "Film Contest", "Dance Showcase", "Physics Olympiad", "Quiz Contest", "E-sports League", "Chess Masters", "Coding Competition", "Math Bowl", "Science Quiz", "Debate League", "Art Expo", "Robotics Expo", "Spelling Challenge", "Basketball League", "Soccer Cup", "Crossword Puzzle Tournament", "Music Concert", "Cooking Showdown", "Poetry Competition", "Film Showcase", "Dance Fest", "Physics Challenge", "Quiz Show", "E-sports Championship", "Chess Showdown", "Coding Challenge", "Math Tournament", "Science Bee", "Debate Showdown", "Art Gala", "Robotics Show", "Spelling Showdown", "Basketball Cup", "Soccer Showcase", "Crossword Puzzle Bowl", "Music Show", "Cooking Bowl", "Poetry Championship", "Film Gala", "Dance Gala", "Physics Contest", "Quiz Gala", "E-sports Fest", "Chess Challenge", "Coding Cup", "Math Showcase", "Science Cup", "Debate Gala", "Art Showdown", "Robotics Championship", "Spelling Bowl", "Basketball Fest", "Soccer Gala", "Crossword Puzzle Show", "Music Bowl", "Cooking Gala", "Poetry Fest", "Film Cup", "Dance Tournament", "Physics Show", "Quiz Showcase", "E-sports Showdown"];
  
  let teacherNames = [];
  let studentNames = [];
  
  let a = 0;
  for (let firstName_index=0; firstName_index<10; ++firstName_index) {
    for (let lastName_index=0; lastName_index<10; ++lastName_index) {
      let username = firstNames[firstName_index]+lastNames[lastName_index];
      let email = ""
  
      if (a%7==0) {
        email = firstNames[firstName_index].toLowerCase()+"."+lastNames[lastName_index].toLowerCase()+"@trinityschoolnyc.org";
        teacherNames.push(firstNames[firstName_index]+" "+lastNames[lastName_index])
      } else if (a%7==1) {
        email = firstNames[firstName_index].toLowerCase()+"."+lastNames[lastName_index].toLowerCase()+"28@trinityschoolnyc.org";
        studentNames.push(firstNames[firstName_index]+" "+lastNames[lastName_index])
      } else if (a%7==2) {
        email = firstNames[firstName_index].toLowerCase()+"."+lastNames[lastName_index].toLowerCase()+"27@trinityschoolnyc.org";
        studentNames.push(firstNames[firstName_index]+" "+lastNames[lastName_index])
      } else if (a%7==3) {
        email = firstNames[firstName_index].toLowerCase()+"."+lastNames[lastName_index].toLowerCase()+"26@trinityschoolnyc.org";
        studentNames.push(firstNames[firstName_index]+" "+lastNames[lastName_index])
      } else if (a%7==4) {
        email = firstNames[firstName_index].toLowerCase()+"."+lastNames[lastName_index].toLowerCase()+"25@trinityschoolnyc.org";
        studentNames.push(firstNames[firstName_index]+" "+lastNames[lastName_index])
      } else if (a%7==5) {
        email = firstNames[firstName_index].toLowerCase()+"."+lastNames[lastName_index].toLowerCase()+"24@trinityschoolnyc.org";
        studentNames.push(firstNames[firstName_index]+" "+lastNames[lastName_index])
      } else if (a%7==6) {
        email = firstNames[firstName_index].toLowerCase()+"."+lastNames[lastName_index].toLowerCase()+"23@trinityschoolnyc.org";
      }
      
      if (username=="DanielIofin") {
        email = "daniel.iofin26@trinityschoolnyc.org"
      } else if (username=="NicholasHutfilz") {
        email = "nicholas.hutfilz25@trinityschoolnyc.org"
      } else if (username=="MadhavendraThakur") {
        email = "madhavendra.thakur26@trinityschoolnyc.org"
      }
  
      async function createAccount(){
        await fetch("http://127.0.0.1:3001/api/user/handleLogin", {
          method: "POST",
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({"email": email})
        })
      }
      await createAccount();
      ++a;
    }
  }
  
  console.log(teacherNames.length+" teachers created, "+studentNames.length+" students created, "+Number(studentNames.length+teacherNames.length)+" total users created.")  
  
  let clubTypes = ["General", "General", "Affinity", "Publication", "Forensic", "Performing Art", "Service"];
  let publicationEndings = [' times', ' gazette', ' newsletter', ' digest', ' journal', ' newspaper']
  let performingArtsEndings = [' performing group', ' theatrical group', ' singing group', ' circus']
  
  let clubNames = []
  
  let b=0;
  for (let club_index=0; club_index<100; ++club_index) {
    let clubName = "";
    let clubType = clubTypes[b%7];
    let facultyAdvisor = teacherNames[club_index%teacherNames.length];
    let studentLeader1 = "";
    let studentLeader2 = "";
    let studentLeader3 = "";
    let studentLeaders = [];
  
    if (b%3==0) {
      studentLeader1 = studentNames[Math.round(Math.random()*(studentNames.length-1))];
      studentLeader2 = studentNames[Math.round(Math.random()*(studentNames.length-1))];
      studentLeader3 = studentNames[Math.round(Math.random()*(studentNames.length-1))];
  
      while (studentLeader2==studentLeader1) {
        studentLeader2 = studentNames[Math.round(Math.random()*(studentNames.length-1))];
      }
      while (studentLeader3==studentLeader1 || studentLeader3==studentLeader2) {
        studentLeader3 = studentNames[Math.round(Math.random()*(studentNames.length-1))];
      }

      studentLeaders = [studentLeader1, studentLeader2, studentLeader3];
    }
    if (b%3==1) {
      studentLeader1 = studentNames[Math.round(Math.random()*(studentNames.length-1))];
      studentLeader2 = studentNames[Math.round(Math.random()*(studentNames.length-1))];
  
      while (studentLeader2==studentLeader1) {
        studentLeader2 = studentNames[Math.round(Math.random()*(studentNames.length-1))];
      }

      studentLeaders = [studentLeader1, studentLeader2];
    }
    if (b%3==2) {
      studentLeader1 = studentNames[Math.round(Math.random()*(studentNames.length-1))];

      studentLeaders = [studentLeader1];
    }
  
    if (b%7==0 || b%7==1){
      clubName = nouns[b]+" club";
    }
    if (b%7==2) {
      clubName = nouns[b]+" affinity group";
    }
    if (b%7==3) {
      clubName = nouns[b]+publicationEndings[b%6];
    }
    if (b%7==4) {
      clubName = "competitive "+nouns[b]+" team";
    }
    if (b%7==5) {
      clubName = nouns[b]+performingArtsEndings[b%4];
    }
    if (b%7==6) {
      clubName = nouns[b]+" service group"
    }
  
    clubNames.push(clubName);
  
    async function createClub(){
      await fetch("http://127.0.0.1:3001/api/admin/clubs/all", {
        method: "POST",
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({"name": clubName, "type": clubType, "facultyAdvisor": facultyAdvisor, "studentLeaders": studentLeaders})
      })
    }
    await createClub();
    ++b;
  }
  console.log(clubNames.length+" clubs created.")  
  
  let clubsJoined = []
  let c=0
  for (let student_index=0; student_index<studentNames.length; ++student_index) {
    let officialName = studentNames[student_index].replace(" ", "%20");
  
    let clubJoinIndex=0;
    clubJoinIndex += Math.round(Math.random()*200)
    while (clubJoinIndex<clubNames.length) {
      let clubName = clubNames[clubJoinIndex].replace(" ", "%20");
      clubsJoined.push(officialName+" →→→ "+clubName)
  
      async function joinClub(){
        await fetch("http://127.0.0.1:3001/api/user/club/join", {
          method: "POST",
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({"officialName": officialName, "clubName": clubName})
        })
      }
      await joinClub();
      ++c;
      clubJoinIndex += Math.round(Math.random()*200);
  
    }
  }
  console.log(clubsJoined.length+" users joined clubs.")
  
  let clubMeetings = []
  let d=0;
  for (let club_index=0; club_index<clubNames.length; ++club_index) {
    let clubName = clubNames[club_index].replace(" ", "%20");
    let meetingsToAdd = 11+(d%4);
  
    for (let meeting_index=0; meeting_index<meetingsToAdd; ++meeting_index) {
      let dayOfMonth = Math.round(Math.random()*29+1);
  
      let meetingDate = "2024-"+(10+d%3)+"-"+dayOfMonth;
  
      let minute = (d%60).toString();
      if (minute.length==1) {
        minute = "0"+minute;
      }
      let startHour = (d%23).toString();
      if (startHour.length==1) {
        startHour = "0"+startHour;
      }
      let endHour = (d%23+1).toString();
      if (endHour.length==1) {
        endHour = "0"+endHour;
      }
      let meetingStartTime = startHour+":"+minute;
      let meetingEndTime = endHour+":"+minute;
  
      let isAdhoc = Boolean(Math.round(Math.random()))
  
      let roomNumber = (d%30+1).toString();
      if (roomNumber.length==1) {
        roomNumber = "0"+roomNumber;
      }
      let meetingLocation = "N-3"+roomNumber;
      let visibility = Boolean(Math.round(Math.random()));
  
      let meetingObject = {"clubName": clubName, "date": meetingDate, "startTime": meetingStartTime, "endTime": meetingEndTime, "adHocMeeting": isAdhoc, "location": meetingLocation, "visibility": visibility}
      clubMeetings.push(clubName+": "+JSON.stringify(meetingObject))
  
      async function addMeeting(){
        return await fetch("http://127.0.0.1:3001/api/clubLeader/"+clubName+"/meetings", {
          method: "POST",
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(meetingObject)
        })
      }
      let meeting = await addMeeting();

      async function approveMeeting(id){
        return await fetch("http://127.0.0.1:3001/api/admin/meeting/"+id+"/approve", {
          method: "PUT",
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(meetingObject)
        })
      }
      async function denyMeeting(id){
        return await fetch("http://127.0.0.1:3001/api/admin/meeting/"+id+"/deny", {
          method: "PUT",
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(meetingObject)
        })
      }
      
      let meetingId = (await meeting.json()).id;
      if (meetingId%3==0) {
        await approveMeeting(meetingId)
      }
      if (meetingId%3==1) {
        await denyMeeting(meetingId)
      }
      ++d;
    }
  }
  
  console.log(clubMeetings.length+" meetings created.")
  
  
  let meetingsJoined = []
  let e=0;
  for (let student_index=0; student_index<studentNames.length; ++student_index) {
    let meetingJoin_index=0;
    meetingJoin_index += Math.round(Math.random()*100000000)//Temporarily set to a high number because users not yet being added to meetings
    while (meetingJoin_index<clubNames.length) {
      let officialName = studentNames[student_index]
      let clubName = clubNames[meetingJoin_index];
      meetingsJoined.push(officialName+" →→→ "+clubName)
      let meetingObject = {"officialName": officialName, "clubName": clubName, "idHash":""}
  
      async function joinMeeting(){
        await fetch("http://127.0.0.1:3001/api/user/meeting/attend", {
          method: "POST",
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(meetingObject)
        })
      }
      await joinMeeting();
      meetingJoin_index += Math.round(Math.random()*10);
      ++e;
    }
  }
  console.log(meetingsJoined.length+" meetings joined.")  
  
  let communicationsCreated = []
  let f=0;
  for (let club_index=0; club_index<clubNames.length; ++club_index) {
    let clubCommunication_index=0;
    let clubName = clubNames[club_index];
    while (clubCommunication_index<Math.round(Math.random()*20)) {
      let message = competitions[clubCommunication_index]+" important communication."
      communicationsCreated.push(message+" →→→ "+clubName)
      let communicationObject = {"clubName": clubName, "subject": "read now", "message": message}
  
      async function addCommunication(){
        return await fetch("http://127.0.0.1:3001/api/clubLeader/"+clubName+"/communication", {
          method: "POST",
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(communicationObject)
        })
      }
      let communication = await addCommunication();

      async function approveCommunication(id){
        return await fetch("http://127.0.0.1:3001/api/admin/communication/"+id+"/approve", {
          method: "PUT",
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(communicationObject)
        })
      }
      async function denyCommunication(id){
        return await fetch("http://127.0.0.1:3001/api/admin/communication/"+id+"/deny", {
          method: "PUT",
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(communicationObject)
        })
      }
      
      let communicationId = (await communication.json()).id;
      if (communicationId%3==0) {
        await approveCommunication(communicationId)
      }
      if (communicationId%3==1) {
        await denyCommunication(communicationId)
      }

      clubCommunication_index += Math.round(Math.random()*9);
      ++f;
    }
  }
  console.log(communicationsCreated.length+" communications created.");

  async function getAllData(){
    return await fetch("http://127.0.0.1:3001/api/developer/data/download", {
      method: "GET",
      headers: {'Content-Type': 'application/json'},
    })
  }
  console.log("All data:");
  console.log(await (await getAllData()).json());

  
}

fillDB();