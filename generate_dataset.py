"""
generate_dataset.py
--------------------
One-time utility script used to build data/books.csv.
Not required to run the app (books.csv is already generated),
but kept in the repo so the dataset is fully reproducible/transparent.
"""

import csv
import random
import os

random.seed(42)

# (title, author, genre, language, year, pages, publisher, description)
BOOKS = [
    ("Atomic Habits", "James Clear", "Self Help", "English", 2018, 320, "Avery", "A practical guide to building good habits and breaking bad ones through small, incremental changes."),
    ("The Psychology of Money", "Morgan Housel", "Business", "English", 2020, 256, "Harriman House", "Timeless lessons on wealth, greed, and happiness told through short, memorable stories."),
    ("Deep Work", "Cal Newport", "Business", "English", 2016, 296, "Grand Central Publishing", "A guide to focused success in a distracted world through the practice of deep, undistracted work."),
    ("Sapiens", "Yuval Noah Harari", "History", "English", 2011, 443, "Harper", "A sweeping narrative of how Homo sapiens came to dominate the world through myths, cooperation, and revolutions."),
    ("Homo Deus", "Yuval Noah Harari", "History", "English", 2016, 450, "Harper", "An exploration of humanity's future as technology reshapes biology, consciousness, and society."),
    ("Educated", "Tara Westover", "Biography", "English", 2018, 334, "Random House", "A memoir of a woman who grows up in a survivalist family and eventually earns a PhD from Cambridge."),
    ("Becoming", "Michelle Obama", "Biography", "English", 2018, 448, "Crown", "An intimate memoir chronicling the former First Lady's journey from Chicago's South Side to the White House."),
    ("The Alchemist", "Paulo Coelho", "Fiction", "English", 1988, 208, "HarperOne", "A shepherd boy travels to Egypt in search of treasure, discovering the importance of following one's dreams."),
    ("1984", "George Orwell", "Fiction", "English", 1949, 328, "Secker & Warburg", "A dystopian vision of a totalitarian future where the Party controls truth, thought, and history."),
    ("Animal Farm", "George Orwell", "Fiction", "English", 1945, 112, "Secker & Warburg", "A satirical fable about farm animals who overthrow their human owner, only to fall under new tyranny."),
    ("To Kill a Mockingbird", "Harper Lee", "Fiction", "English", 1960, 281, "J.B. Lippincott & Co.", "A young girl in the American South witnesses her father defend a black man falsely accused of rape."),
    ("The Great Gatsby", "F. Scott Fitzgerald", "Classic", "English", 1925, 180, "Charles Scribner's Sons", "A tragic tale of wealth, love, and the American Dream set in the Jazz Age of Long Island."),
    ("Pride and Prejudice", "Jane Austen", "Romance", "English", 1813, 279, "T. Egerton", "A witty exploration of manners, marriage, and misunderstanding in Georgian England."),
    ("Wuthering Heights", "Emily Bronte", "Romance", "English", 1847, 342, "Thomas Cautley Newby", "A dark, passionate tale of love and revenge on the English moors."),
    ("Jane Eyre", "Charlotte Bronte", "Romance", "English", 1847, 500, "Smith, Elder & Co.", "An orphaned governess finds love and independence despite hardship and injustice."),
    ("The Hobbit", "J.R.R. Tolkien", "Fantasy", "English", 1937, 310, "George Allen & Unwin", "A reluctant hobbit joins a company of dwarves on a quest to reclaim treasure from a dragon."),
    ("The Fellowship of the Ring", "J.R.R. Tolkien", "Fantasy", "English", 1954, 423, "George Allen & Unwin", "A hobbit sets out on a perilous journey to destroy a powerful, corrupting ring."),
    ("Harry Potter and the Sorcerer's Stone", "J.K. Rowling", "Fantasy", "English", 1997, 309, "Bloomsbury", "A young boy discovers he is a wizard and begins his journey at a magical school."),
    ("A Game of Thrones", "George R.R. Martin", "Fantasy", "English", 1996, 694, "Bantam Spectra", "Noble families vie for control of the Iron Throne in a land where winter is coming."),
    ("The Name of the Wind", "Patrick Rothfuss", "Fantasy", "English", 2007, 662, "DAW Books", "A legendary figure recounts his youth as a gifted magician and reluctant hero."),
    ("Mistborn: The Final Empire", "Brandon Sanderson", "Fantasy", "English", 2006, 541, "Tor Books", "A young thief with rare magical powers joins a rebellion against an immortal emperor."),
    ("Dune", "Frank Herbert", "Science Fiction", "English", 1965, 412, "Chilton Books", "A young noble navigates politics, prophecy, and survival on a harsh desert planet rich in a valuable spice."),
    ("Foundation", "Isaac Asimov", "Science Fiction", "English", 1951, 255, "Gnome Press", "A mathematician predicts the fall of a galactic empire and sets a plan to shorten the coming dark age."),
    ("Neuromancer", "William Gibson", "Science Fiction", "English", 1984, 271, "Ace Books", "A washed-up hacker is hired for one last job in a gritty, cyberpunk future."),
    ("Ender's Game", "Orson Scott Card", "Science Fiction", "English", 1985, 324, "Tor Books", "A gifted child is trained to lead humanity's fleet against an alien threat."),
    ("The Martian", "Andy Weir", "Science Fiction", "English", 2011, 369, "Crown", "An astronaut stranded on Mars must use science and ingenuity to survive."),
    ("Brave New World", "Aldous Huxley", "Science Fiction", "English", 1932, 311, "Chatto & Windus", "A genetically engineered society pursues pleasure and stability at the cost of freedom and individuality."),
    ("Fahrenheit 451", "Ray Bradbury", "Science Fiction", "English", 1953, 194, "Ballantine Books", "In a future where books are banned, a fireman tasked with burning them begins to question his world."),
    ("The Girl with the Dragon Tattoo", "Stieg Larsson", "Thriller", "English", 2005, 465, "Norstedts Förlag", "A disgraced journalist and a brilliant hacker investigate a decades-old disappearance."),
    ("Gone Girl", "Gillian Flynn", "Thriller", "English", 2012, 415, "Crown", "A woman's disappearance on her anniversary reveals dark secrets in her marriage."),
    ("The Da Vinci Code", "Dan Brown", "Thriller", "English", 2003, 454, "Doubleday", "A symbologist unravels a religious mystery hidden within famous works of art."),
    ("And Then There Were None", "Agatha Christie", "Mystery", "English", 1939, 272, "Collins Crime Club", "Ten strangers are lured to an island where they are killed one by one."),
    ("The Murder of Roger Ackroyd", "Agatha Christie", "Mystery", "English", 1926, 312, "William Collins & Sons", "Detective Poirot investigates a murder in a quiet English village with a shocking twist."),
    ("Sherlock Holmes: A Study in Scarlet", "Arthur Conan Doyle", "Mystery", "English", 1887, 154, "Ward Lock & Co.", "The introduction of detective Sherlock Holmes as he solves a baffling London murder."),
    ("It", "Stephen King", "Horror", "English", 1986, 1138, "Viking", "A group of children face an ancient, shape-shifting evil terrorizing their town."),
    ("The Shining", "Stephen King", "Horror", "English", 1977, 447, "Doubleday", "A family becomes caretakers of an isolated hotel with a sinister, supernatural presence."),
    ("Dracula", "Bram Stoker", "Horror", "English", 1897, 418, "Archibald Constable and Company", "A vampire's arrival in England leads to a battle between the undead and a group of determined hunters."),
    ("Frankenstein", "Mary Shelley", "Horror", "English", 1818, 280, "Lackington, Hughes, Harding, Mavor & Jones", "A scientist creates life from dead tissue, only to be haunted by his own creation."),
    ("The Fault in Our Stars", "John Green", "Young Adult", "English", 2012, 313, "Dutton Books", "Two teenagers with cancer fall in love while grappling with mortality and meaning."),
    ("The Hunger Games", "Suzanne Collins", "Young Adult", "English", 2008, 374, "Scholastic Press", "A girl volunteers to fight in a televised death match to save her sister in a dystopian nation."),
    ("Divergent", "Veronica Roth", "Young Adult", "English", 2011, 487, "Katherine Tegen Books", "A teenage girl discovers she doesn't fit into any single faction of her divided society."),
    ("The Perks of Being a Wallflower", "Stephen Chbosky", "Young Adult", "English", 1999, 213, "MTV Books", "A shy teenager navigates friendship, love, and trauma through letters to an anonymous friend."),
    ("Thinking, Fast and Slow", "Daniel Kahneman", "Psychology", "English", 2011, 499, "Farrar, Straus and Giroux", "A Nobel laureate explains the two systems that drive human thought and decision-making."),
    ("Man's Search for Meaning", "Viktor E. Frankl", "Psychology", "English", 1946, 165, "Beacon Press", "A psychiatrist's account of surviving the Holocaust and discovering purpose through suffering."),
    ("The Power of Habit", "Charles Duhigg", "Psychology", "English", 2012, 371, "Random House", "An exploration of the science behind why habits exist and how they can be changed."),
    ("Quiet", "Susan Cain", "Psychology", "English", 2012, 333, "Crown", "A case for the undervalued power of introverts in an extroverted world."),
    ("Sapiens: A Graphic History", "Yuval Noah Harari", "History", "English", 2020, 256, "Harper", "A vivid illustrated adaptation exploring the origins of human civilization."),
    ("Guns, Germs, and Steel", "Jared Diamond", "History", "English", 1997, 480, "W. W. Norton & Company", "An examination of why some civilizations conquered others through geography, biology, and technology."),
    ("The Diary of a Young Girl", "Anne Frank", "Biography", "English", 1947, 283, "Contact Publishing", "The poignant wartime diary of a Jewish teenager hiding from the Nazis in Amsterdam."),
    ("Steve Jobs", "Walter Isaacson", "Biography", "English", 2011, 656, "Simon & Schuster", "A comprehensive biography of the visionary co-founder of Apple, based on exclusive interviews."),
    ("Elon Musk", "Walter Isaacson", "Biography", "English", 2023, 688, "Simon & Schuster", "An in-depth biography exploring the ambitions and controversies of the entrepreneur behind Tesla and SpaceX."),
    ("Shoe Dog", "Phil Knight", "Business", "English", 2016, 400, "Scribner", "The candid memoir of Nike's founder and the early struggles of building a global brand."),
    ("Zero to One", "Peter Thiel", "Business", "English", 2014, 224, "Crown Business", "A contrarian guide to building startups that create new markets rather than competing in old ones."),
    ("The Lean Startup", "Eric Ries", "Business", "English", 2011, 336, "Crown Business", "A methodology for developing businesses through validated learning and rapid iteration."),
    ("Rich Dad Poor Dad", "Robert Kiyosaki", "Business", "English", 1997, 336, "Warner Books", "A personal finance classic contrasting two mindsets toward money, assets, and wealth building."),
    ("Good to Great", "Jim Collins", "Business", "English", 2001, 300, "HarperBusiness", "A research-based study of what separates good companies from truly great ones."),
    ("Artificial Intelligence: A Modern Approach", "Stuart Russell", "Technology", "English", 1995, 1152, "Prentice Hall", "The definitive textbook covering the theory and practice of modern artificial intelligence."),
    ("Deep Learning", "Ian Goodfellow", "Technology", "English", 2016, 800, "MIT Press", "A comprehensive introduction to deep learning covering theory, algorithms, and applications."),
    ("The Innovators", "Walter Isaacson", "Technology", "English", 2014, 542, "Simon & Schuster", "The story of the people who built the computer and the internet, from Ada Lovelace to Silicon Valley."),
    ("Clean Code", "Robert C. Martin", "Technology", "English", 2008, 464, "Prentice Hall", "A guide to writing readable, maintainable, and elegant software through disciplined practices."),
    ("The Pragmatic Programmer", "Andrew Hunt", "Technology", "English", 1999, 352, "Addison-Wesley", "Practical advice for software developers on craftsmanship, tools, and career growth."),
    ("Life 3.0", "Max Tegmark", "AI", "English", 2017, 384, "Knopf", "An exploration of what artificial intelligence means for the future of life on Earth and beyond."),
    ("Superintelligence", "Nick Bostrom", "AI", "English", 2014, 328, "Oxford University Press", "An analysis of the potential paths, dangers, and strategies surrounding superintelligent AI."),
    ("Human Compatible", "Stuart Russell", "AI", "English", 2019, 336, "Viking", "A leading AI researcher proposes a new approach to keep intelligent machines aligned with human values."),
    ("The Alignment Problem", "Brian Christian", "AI", "English", 2020, 496, "W. W. Norton & Company", "An investigation into how machine learning systems can be made to reflect genuine human values."),
    ("A Brief History of Time", "Stephen Hawking", "Science", "English", 1988, 256, "Bantam Books", "An accessible exploration of cosmology, black holes, and the origins of the universe."),
    ("Cosmos", "Carl Sagan", "Science", "English", 1980, 365, "Random House", "A journey through the universe blending astronomy, history, and philosophy."),
    ("The Selfish Gene", "Richard Dawkins", "Science", "English", 1976, 224, "Oxford University Press", "A gene-centered view of evolution that reshaped how biologists understand natural selection."),
    ("Astrophysics for People in a Hurry", "Neil deGrasse Tyson", "Science", "English", 2017, 224, "W. W. Norton & Company", "A concise, accessible tour of the cosmos for readers short on time but curious about everything."),
    ("The Origin of Species", "Charles Darwin", "Science", "English", 1859, 502, "John Murray", "The foundational text introducing the theory of evolution through natural selection."),
    ("Meditations", "Marcus Aurelius", "Philosophy", "English", 180, 254, "Public Domain", "The private reflections of a Roman emperor on virtue, duty, and the nature of life."),
    ("The Republic", "Plato", "Philosophy", "English", -380, 416, "Public Domain", "A Socratic dialogue examining justice, the ideal state, and the nature of the philosopher-king."),
    ("Beyond Good and Evil", "Friedrich Nietzsche", "Philosophy", "English", 1886, 240, "C. G. Naumann", "A critique of past philosophers and traditional morality, proposing a new philosophy of power."),
    ("The Stranger", "Albert Camus", "Philosophy", "French", 1942, 123, "Gallimard", "A detached man's indifferent reaction to his mother's death leads to a fateful, absurd crime."),
    ("Man and His Symbols", "Carl Jung", "Psychology", "English", 1964, 320, "Doubleday", "An accessible introduction to Jung's theories of the unconscious and the meaning of dreams."),
    ("One Hundred Years of Solitude", "Gabriel Garcia Marquez", "Fiction", "Spanish", 1967, 417, "Harper & Row", "A multigenerational saga of the Buendia family in the mythical town of Macondo."),
    ("Love in the Time of Cholera", "Gabriel Garcia Marquez", "Romance", "Spanish", 1985, 348, "Editorial Oveja Negra", "A decades-spanning tale of unrequited love, patience, and devotion."),
    ("The Little Prince", "Antoine de Saint-Exupery", "Fiction", "French", 1943, 96, "Reynal & Hitchcock", "A stranded pilot meets a young prince who shares tales of his travels and reflections on life."),
    ("Crime and Punishment", "Fyodor Dostoevsky", "Classic", "Russian", 1866, 671, "The Russian Messenger", "A poor student's murder of a pawnbroker spirals into a psychological study of guilt and redemption."),
    ("War and Peace", "Leo Tolstoy", "Classic", "Russian", 1869, 1225, "The Russian Messenger", "An epic chronicle of Russian society during the Napoleonic era, following five aristocratic families."),
    ("Anna Karenina", "Leo Tolstoy", "Classic", "Russian", 1878, 864, "The Russian Messenger", "A tragic tale of love, betrayal, and society in Imperial Russia."),
    ("Don Quixote", "Miguel de Cervantes", "Classic", "Spanish", 1605, 863, "Francisco de Robles", "The adventures of a nobleman who loses his sanity and sets out as a chivalrous knight-errant."),
    ("The Metamorphosis", "Franz Kafka", "Classic", "German", 1915, 96, "Kurt Wolff Verlag", "A traveling salesman wakes to find himself transformed into a giant insect."),
    ("Norwegian Wood", "Haruki Murakami", "Fiction", "Japanese", 1987, 296, "Kodansha", "A nostalgic tale of love and loss among Japanese university students in the 1960s."),
    ("Kafka on the Shore", "Haruki Murakami", "Fiction", "Japanese", 2002, 505, "Shinchosha", "A surreal, dreamlike story following a runaway teenager and an elderly man who talks to cats."),
    ("The Book Thief", "Markus Zusak", "Fiction", "English", 2005, 552, "Picador", "A young girl in Nazi Germany finds solace in stolen books, narrated by Death himself."),
    ("Life of Pi", "Yann Martel", "Fiction", "English", 2001, 319, "Knopf Canada", "A boy survives a shipwreck and is stranded on a lifeboat with a Bengal tiger."),
    ("The Kite Runner", "Khaled Hosseini", "Fiction", "English", 2003, 371, "Riverhead Books", "A story of friendship, guilt, and redemption set against the backdrop of Afghanistan's turmoil."),
    ("A Thousand Splendid Suns", "Khaled Hosseini", "Fiction", "English", 2007, 367, "Riverhead Books", "The intertwined lives of two Afghan women bound by war, sacrifice, and hope."),
    ("The Handmaid's Tale", "Margaret Atwood", "Fiction", "English", 1985, 311, "McClelland & Stewart", "A dystopian society strips women of autonomy in a totalitarian, theocratic regime."),
    ("Beloved", "Toni Morrison", "Fiction", "English", 1987, 324, "Alfred A. Knopf", "A former slave is haunted by the ghost of the daughter she lost, confronting the horrors of slavery."),
    ("The Road", "Cormac McCarthy", "Fiction", "English", 2006, 287, "Alfred A. Knopf", "A father and son journey through a desolate, post-apocalyptic America in search of survival."),
    ("Slaughterhouse-Five", "Kurt Vonnegut", "Science Fiction", "English", 1969, 275, "Delacorte Press", "A soldier becomes unstuck in time, reliving the firebombing of Dresden and encounters with aliens."),
    ("Catch-22", "Joseph Heller", "Fiction", "English", 1961, 453, "Simon & Schuster", "A satirical look at the absurdity and bureaucracy of war through the eyes of a bombardier."),
    ("The Catcher in the Rye", "J.D. Salinger", "Fiction", "English", 1951, 277, "Little, Brown and Company", "A disillusioned teenager wanders New York City reflecting on innocence and phoniness."),
    ("Lord of the Flies", "William Golding", "Fiction", "English", 1954, 224, "Faber and Faber", "Stranded boys descend into savagery as they attempt to govern themselves on a deserted island."),
    ("Brave New Habits", "Nir Eyal", "Self Help", "English", 2019, 256, "BenBella Books", "Practical strategies for staying focused and building indistractable habits in a noisy world."),
    ("The 7 Habits of Highly Effective People", "Stephen R. Covey", "Self Help", "English", 1989, 381, "Free Press", "A principle-centered approach to personal and professional effectiveness."),
    ("How to Win Friends and Influence People", "Dale Carnegie", "Self Help", "English", 1936, 291, "Simon & Schuster", "Timeless advice on building relationships, persuasion, and effective communication."),
    ("The Subtle Art of Not Giving a F*ck", "Mark Manson", "Self Help", "English", 2016, 224, "HarperOne", "A counterintuitive approach to living a good life by focusing only on what truly matters."),
    ("Can't Hurt Me", "David Goggins", "Self Help", "English", 2018, 364, "Lioncrest Publishing", "A former Navy SEAL's account of overcoming adversity through extreme mental toughness."),
    ("Ikigai", "Hector Garcia", "Self Help", "Spanish", 2016, 208, "Penguin Life", "A Japanese concept of finding purpose at the intersection of passion, mission, vocation, and profession."),
    ("The Midnight Library", "Matt Haig", "Fiction", "English", 2020, 304, "Canongate Books", "A woman explores infinite alternate lives through a mysterious library between life and death."),
    ("Where the Crawdads Sing", "Delia Owens", "Fiction", "English", 2018, 384, "G.P. Putnam's Sons", "A reclusive girl raised in the marshes becomes a murder suspect in a small coastal town."),
    ("Verity", "Colleen Hoover", "Romance", "English", 2018, 336, "Grand Central Publishing", "A struggling writer uncovers dark secrets while finishing a bestselling author's final book series."),
    ("It Ends with Us", "Colleen Hoover", "Romance", "English", 2016, 384, "Atria Books", "A woman confronts painful truths about love, family, and breaking generational cycles."),
    ("The Seven Husbands of Evelyn Hugo", "Taylor Jenkins Reid", "Romance", "English", 2017, 400, "Atria Books", "A reclusive Hollywood icon finally reveals the truth of her extraordinary and scandalous life."),
    ("Project Hail Mary", "Andy Weir", "Science Fiction", "English", 2021, 476, "Ballantine Books", "A lone astronaut wakes with no memory, tasked with saving humanity from extinction."),
    ("Klara and the Sun", "Kazuo Ishiguro", "Science Fiction", "English", 2021, 303, "Faber and Faber", "An artificial friend observes and learns about human love, loneliness, and hope."),
    ("The Silent Patient", "Alex Michaelides", "Thriller", "English", 2019, 336, "Celadon Books", "A woman's shocking act of violence and her subsequent silence unravel in a gripping psychological thriller."),
    ("Atomic Design", "Brad Frost", "Technology", "English", 2016, 145, "Self-Published", "A methodology for creating design systems using reusable, composable interface components."),
    ("Designing Data-Intensive Applications", "Martin Kleppmann", "Technology", "English", 2017, 616, "O'Reilly Media", "A deep dive into the architecture and trade-offs behind reliable, scalable data systems."),
    ("You Don't Know JS", "Kyle Simpson", "Technology", "English", 2015, 278, "O'Reilly Media", "A deep exploration of the core mechanisms of the JavaScript language."),
    ("Hands-On Machine Learning", "Aurelien Geron", "AI", "English", 2017, 851, "O'Reilly Media", "A practical guide to building machine learning systems using Scikit-Learn, Keras, and TensorFlow."),
    ("The Hundred-Page Machine Learning Book", "Andriy Burkov", "AI", "English", 2019, 160, "Andriy Burkov", "A concise, accessible overview of the essential concepts in machine learning."),
]

GENRES = sorted(set(b[2] for b in BOOKS))

def compute_metrics(idx: int, year: int):
    """Deterministically derive rating, num_ratings, and popularity for a book."""
    base_rating = round(random.uniform(3.5, 4.9), 2)
    num_ratings = random.randint(500, 250000)
    # Newer + more ratings + higher rating => higher popularity
    recency_boost = max(0, (year - 1950)) / (2026 - 1950) if year > 0 else 0
    popularity = round(
        min(100, (base_rating / 5 * 40) + (min(num_ratings, 200000) / 200000 * 40) + (recency_boost * 20)),
        1,
    )
    return base_rating, num_ratings, popularity


def main():
    out_path = os.path.join(os.path.dirname(__file__), "data", "books.csv")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    fieldnames = [
        "book_id", "title", "author", "genre", "language", "publication_year",
        "average_rating", "num_ratings", "popularity_score", "num_pages",
        "description", "publisher",
    ]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i, (title, author, genre, language, year, pages, publisher, desc) in enumerate(BOOKS, start=1):
            rating, num_ratings, popularity = compute_metrics(i, year)
            writer.writerow({
                "book_id": i,
                "title": title,
                "author": author,
                "genre": genre,
                "language": language,
                "publication_year": year,
                "average_rating": rating,
                "num_ratings": num_ratings,
                "popularity_score": popularity,
                "num_pages": pages,
                "description": desc,
                "publisher": publisher,
            })

    print(f"Wrote {len(BOOKS)} books to {out_path}")


if __name__ == "__main__":
    main()
