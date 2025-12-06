# Group reflection

## Summary of feedback on our tool

Overall, the feedback on our tool was very positive. The other groups found it useful and liked the clarity provided in the README and the video we included. At the same time, they also pointed out areas where the tool could be expanded or improved in the future. 

One point was, that our tool currently assumes all existing psets in the IFC model to be correct. The suggestion was to add a check that compares the existing pset values for the airflow with the airflow calculated in the script. If the match is too large, the script could flag this as an issue and add it to the BCF file. This would add a layer of quality check and make the tool more robust.

Another comment suggested that we might consider adding the pressure loss results to the BCF issues. At this point, the pressure loss is calculated but not used to create issues. Making it a part of the BCF file could help engineers with understanding where critical pressure loss occur in the model. 

We also received suggestions about expanding the tool to handle flowsegments or pipes, which could make the tool applicable beyond ventilation systems. 

**Did the tool address the use case we identified?**

Yes, the tool succeeded to address the use case we identified ... 


**What stage does the tool you created work in Advanced Building Design (stage A, B, C and/ or D)?**

---
# Individual reflections

## Katrine Aarup Nielsen - s214310

### Your learning experience for the concept you focused on.

At the beginning of the course I would describe myself mainly as a modeller, with focus on making a building look correct within a BIM software. Now, after working with IFC data and scripting, I have gotten insights into how much values the underlying data and information in the BIM models have, and how in can be used for analysis and validation. I would therefore now identify myself as more of an analyst than a modeller. 

There is still a lot I need to learn, especially when it comes to creating more advanced scripts, handling complex IFC files and understanding larger BIM workflows. I also want to develop a better overview of how to structure tools better so they are more scalable and easier to maintain. But I can see, that with more practice, and the right idea or use case, I would be able to create tools that makes BIM workflows more effective and efficient. 

In the future, I would like to use BIM more actively to check models in the process, as it can save a lot of time and reduce errors, both in my own work and hen receiving models from others. 

### Your process of developing the tutorial

The process of developing the tutorial helped me understand what we were building and why each step mattered. Writing things down made the workflow more concrete, and it also showed me which parts I understood well and which parts needed more clarification. In that way, the course process helped me define possible questions to explore later, such as how automated model checking could be integrated into design workflows, which is something I could potentially use in my thesis. 

I think the freedom we had in choosing our own use case was good. It allowed us to work with something we found interesting, which made the project more motivating. It also gave us space to explore and expand the use case throughout the process, instead of being locked into something fixed from the beginning. 

Regarding the number of tools, I think it was balanced. I did not get to use all the tools we were introduced to, but it was nice to know they were available if needed. It would have been helpful to know from the start that not all tools were required, as it can be quite overvwheldming in the beginning. A short introduction to the course website at the start of the semester would also have been usefulto understand how everything is structured and where to find information. 

### Your future for Advanced use of OpenBIM

I think it is quite likely that I will use OpenBIM in my thesis. The course have shown me how much information can be hidden inside an IFC file and how many possibilities there are for doing check or extracting data that could otherwise be time consuming. If my thesis ends up involving modelling accuracy or system analysing, it would make a lot of sense to include OpenBIM. 

Looking further ahead, I also think I will use OpenBIM tools in my professional life. The industry is moving towards more open workflows, automation and data-driven quality control, and I can see how useful it is to be able to understand what is going on behind the model. Being able to check or extract data myself will definitely be valuable. 

Overall, the journey from A1 to A5 has taken from simply modelling to actually understanding BIM as a data structure and a tool for analysis. Each assignment added a different layer, from learning the basics of IFC to experimenting with data, building a tool and tutorial, and finally reflecting on the whole process. I now feel more confident working with these kinds of formats, scripts and model checking. 

## Teitur Heinesen - s201348

### Your learning experience for the concept you focused on.
At the beginning of the course, I would describe myself mostly as a _Modeller_ when it came to BIM. I have learned a lot about the intricacies of IFC models and the possibilities they can provide when used as an analytical tool. Going into this course, I don't really think I understood what the IFC-file format offered and after using a lot of time exploring the possibilities they provide, I know how great the opportunities are for future digitilization of almost all fields using BIM models.

I also understand how much more there is to learn and I am eager to try to incorporate free and open-source solutions in future work flows when possible. I also know how prone to errors BIM models can be, be it missing PSETs, wrong physical dimensions, elements clashing (or not clashing, when they need to be) and so on... 

Essentially, it is a good practice to doubt most, if not all parts of a recieved BIM model and being flexible, as almost every part of the models can (and will undoubtedly) change multiple times.

Therefore it is good to be able to develop tools that don't depend solely on manual interactions, but make use of automation, i.e. an analysis that runs every time an IFC file is updated on the cloud service used to colaborate. 

I feel like I ended up as a _Self Learner_, as I spent so much time learning about the heaps of data found in IFC-files, how to use them and the shortcomings of the format.

### Your process of developing the tutorial

Develoing the tool and tutorial definitely opened some new doors, that I'll be able to use for my thesis. 

I really liked being able to choose your own case and being able and it motivated me a lot during the course. That being said, I think some groups would gain a lot from having more strictly defined cases so they more easily could see the posibilities there is in the IFC format. I felt a bit like an outsider because I wanted to spend time learning about the IFC format and wanting to provide a useful tool.

I think it would be great to show more of the tools provided, i.e. the voxelization tool, inspiring the students to use them.


### Your future for Advanced use of OpenBIM

As I mentioned earlier, I think some form of OpenBIM is going to have an essential role in the future of the built environment, and I think everyone studying Architectural Engineering (or Civil Engineering for that matter) should at least know what you can use it for. It is a great format for analysing and being able to compare models, even though some fields would only need a fraction of the data in an IFC-file.

A good example of how OpenBIM tools are used in professional settings, is my current student assistant position in a computational fluid dynamics department. We recieve a lot of IFC files, where we only need a simplified version of the geometries present in them. But as the IFC files are way too detailed for out purposes, my colleagues and I are forced to re-model and simplify the geometries ourselves. I therefore think, some of the shortcomings of the IFC format, is that it is _too_ detailed for my colleagues and my CFD purpose. I would imagine that other fields in construction are facing the same problems.

I have begun looking into FOOS solutions for geometry extraction and modification in my spare time and I aspire to use OpenBIM tools for the rest of my education as well as my professional life.

In conclusion, I have learned a lot from this course, that I hope to use for future professional and academic endeavors and have become even more interested in the digitilization and automation of the built environment than I was before.


