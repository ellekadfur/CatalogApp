#!/usr/bin/env python3


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from catalogdb import Base, User, Category, Item


engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

restaurant1 = Category(name="Soccer")
session.add(restaurant1)
session.commit()

restaurant2 = Category(name="Baseketball")
session.add(restaurant2)
session.commit()

restaurant1 = Category(name="Baseball")
session.add(restaurant1)
session.commit()

restaurant1 = Category(name="Frisbee")
session.add(restaurant1)
session.commit()

restaurant1 = Category(name="Snowboarding")
session.add(restaurant1)
session.commit()

restaurant1 = Category(name="Rock Climbing")
session.add(restaurant1)
session.commit()

restaurant1 = Category(name="Foosball")
session.add(restaurant1)
session.commit()

restaurant1 = Category(name="Skating")
session.add(restaurant1)
session.commit()

restaurant1 = Category(name="Hockey")
session.add(restaurant1)
session.commit()


print("Added Categories items!")
