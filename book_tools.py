# This dictionary holds the detailed summaries for the tool.
# Note that the keys must EXACTLY match the titles in 'book_summaries.md'.

book_summaries_dict = {
    "1984": (
        "In George Orwell's chilling dystopia, Winston Smith navigates a world of total "
        "surveillance under the gaze of Big Brother. His job is to rewrite history, but his "
        "spirit rebels. He embarks on a forbidden love affair and a desperate search for "
        "truth, leading to a brutal confrontation with the regime's power in the infamous "
        "Room 101. It's a profound warning about the dangers of totalitarianism and the fragility of freedom."
    ),
    "The Hobbit": (
        "Bilbo Baggins, a comfort-loving hobbit, has his peaceful life turned upside down "
        "by the wizard Gandalf and a band of dwarves. They recruit him for a perilous quest "
        "to reclaim their stolen treasure from Smaug, a fearsome dragon. On this journey, "
        "Bilbo faces trolls, goblins, and giant spiders, discovering a courage and "
        "resourcefulness he never knew he possessed and finding a mysterious, magical ring."
    ),
    "Dune": (
        "Set on the desert planet Arrakis, the sole source of the universe's most valuable "
        "substance, 'melange', Dune follows the young Paul Atreides. His family is given "
        "stewardship of the planet, but is betrayed by their enemies. Paul must "
        "earn the trust of the native Fremen and lead them in a rebellion to restore his family's "
        "honor and control the planet's destiny, a path that will change the course of humanity."
    ),
    "To Kill a Mockingbird": (
        "Told through the innocent eyes of Scout Finch, this story is set in a small, racially "
        "charged town in the American South. Her father, the principled lawyer Atticus Finch, "
        "defends a black man, Tom Robinson, who is falsely accused of raping a white woman. "
        "The novel is a timeless exploration of racial injustice, moral courage, and the loss of innocence."
    ),
    "The Lord of the Rings": (
        "Frodo Baggins, a humble hobbit, inherits the One Ring—an object of immense power crafted "
        "by the Dark Lord Sauron. Guided by the Fellowship, he must undertake a perilous quest "
        "across Middle-earth to reach Mount Doom and destroy the Ring, facing treacherous landscapes, "
        "orcs, and the Ring’s corrupting influence. As allies fall and hope wanes, Frodo and his "
        "loyal friends summon courage and self-sacrifice. It's a sweeping saga of friendship, sacrifice, "
        "and the enduring battle between light and darkness."
    ),
    "Pride and Prejudice": (
        "Elizabeth Bennet navigates the rigid social mores of early 19th-century England as she "
        "clashes with the proud Mr. Darcy. Through witty dialogue and a series of misunderstandings, "
        "both learn to overcome their initial misjudgments. The novel critiques class consciousness "
        "and celebrates personal growth, love, and the importance of reputation."
    ),
    "The Great Gatsby": (
        "In the opulent world of 1920s Long Island, Nick Carraway becomes drawn into the life of "
        "his enigmatic neighbor, Jay Gatsby, whose lavish parties mask an obsessive love for Daisy Buchanan. "
        "Gatsby’s pursuit of the American Dream and his idealized vision of Daisy illuminate the era's "
        "moral emptiness and social stratification. Told through Nick’s reflective narration, it's "
        "a piercing critique of wealth, illusion, and the elusive nature of fulfillment."
    ),
    "Moby Dick": (
        "Captain Ahab commands the whaling ship Pequod on an obsessive mission to hunt Moby Dick, "
        "the giant white sperm whale that maimed him. Narrated by Ishmael, the voyage delves into the "
        "harsh realities of whaling life, philosophical meditations on fate and nature, and the destructive "
        "power of vengeance. As Ahab’s single-minded pursuit endangers his crew, the novel explores themes "
        "of madness and the fraught relationship between man and the natural world."
    ),
    "War and Peace": (
        "Set against the sweeping backdrop of the Napoleonic Wars, War and Peace follows aristocratic Russian "
        "families—most notably the Rostovs and the Bolkonskys—as they navigate love, loss, and the upheavals of history. "
        "Through vivid battle scenes and intimate personal dramas, Tolstoy examines the interplay of fate, free will, "
        "and societal change. It's an expansive meditation on humanity’s search for meaning amidst chaos and the inexorable "
        "march of history."
    ),
    "The Catcher in the Rye": (
        "Narrated by the disenchanted teenager Holden Caulfield, the story follows his aimless wanderings "
        "through New York City after being expelled from prep school. Holden’s cynical outlook and sharp observations "
        "reveal his struggle with alienation, identity, and the 'phoniness' he perceives in the adult world. "
        "As he seeks innocence in a corrupt society, the novel captures the universal angst of adolescence and "
        "the longing to protect purity."
    ),
}

def get_summary_by_title(title: str) -> str:
    """
    Fetches the detailed summary for a given book title from the local dictionary.

    Args:
        title (str): The exact title of the book to look for.

    Returns:
        str: The detailed summary if the book is found, otherwise a message indicating it was not found.
    """
    # This print helps us see when the tool is actually being executed.
    print(f"\n--- TOOL EXECUTED: get_summary_by_title(title='{title}') ---")
    
    # .get() is a safe way to access a dictionary key, providing a default value if the key doesn't exist.
    return book_summaries_dict.get(title, "Sorry, I couldn't find a detailed summary for that exact title.")