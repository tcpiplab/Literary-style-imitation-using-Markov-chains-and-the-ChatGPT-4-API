from textblob import TextBlob
from text_utilities import TextGenerator
from colorama import Fore, Style
from config import Config
from graph_utilities import display_polarity_graph, display_subjectivity_graph


def analyze_sentiment_of_file(training_corpus_filename):
    """
    Analyzes the sentiment of the given text using TextBlob and returns a sentiment polarity score.

    Args:
        training_corpus_filename (str): The input text to analyze for sentiment.

    Returns:
        float: The sentiment polarity score, which ranges from -1.0 (most negative) to 1.0 (most positive).

    Raises:
        Exception: Any exceptions raised during TextBlob analysis will propagate.
    """

    if Config.VERBOSE:
        print(f"{Fore.GREEN}[+] Analyzing sentiment of {training_corpus_filename}{Style.RESET_ALL}")

    # Convert the corpus text to a string and pass it to TextBlob
    corpus_string = TextGenerator.return_corpus_text(training_corpus_filename)

    average_polarity = print_sentiment_analysis_results(corpus_string, training_corpus_filename)

    return average_polarity


def print_sentiment_analysis_results(corpus_string, training_corpus_filename=None):
    # This will print the sentiment of the input string and display the sentiment score graphically.
    # The training corpus filename is optional and will be used to print the sentiment of the input string.

    average_polarity, average_subjectivity = analyze_sentiment_by_sentence(corpus_string)

    # Gather mnemonic sentiment phrases for polarity and subjectivity
    polarity_phrase = interpret_sentiment_polarity(average_polarity)

    subjectivity_phrase = interpret_sentiment_subjectivity(average_subjectivity)

    print("[" + Fore.YELLOW + "SENTIMENT ANALYSIS" + Style.RESET_ALL + "]")

    if training_corpus_filename is not None:

        print(f"    The training corpus {Fore.LIGHTGREEN_EX}{training_corpus_filename}{Style.RESET_ALL}"
              f" is {polarity_phrase} and {subjectivity_phrase}.\n"
              f"    Sentiment Polarity: {Fore.LIGHTBLUE_EX}{average_polarity:>10.4f}{Style.RESET_ALL}", end="      ")

    elif training_corpus_filename is None:
        print(f"    The output text is {polarity_phrase} and {subjectivity_phrase}.\n"
              f"    Sentiment Polarity: {Fore.LIGHTBLUE_EX}{average_polarity:>10.4f}{Style.RESET_ALL}", end="      ")

    display_polarity_graph(average_polarity)

    print(f"    Sentiment Subjectivity: {Fore.LIGHTBLUE_EX}{average_subjectivity:.4f}{Style.RESET_ALL}", end="       ")

    display_subjectivity_graph(average_subjectivity)

    return average_polarity


def analyze_sentiment_of_string(text_string):
    """
    **This function is optimized for analyzing shorter strings.**

    Analyze the overall sentiment of a text string and display the sentiment score.

    The function uses the TextBlob library to analyze the sentiment polarity
    of a text string. It then interprets the sentiment, prints the sentiment and its
    polarity score, and displays the sentiment score graphically.

    Parameters:
        text_string (str): The text string to analyze.

    Returns:
        float: The sentiment polarity of the text string.
    """

    # Instantiate TextBlob and analyze sentiment
    analysis = TextBlob(text_string)

    # Return the polarity score of the analyzed the corpus text string
    sentiment_polarity: float = analysis.sentiment.polarity

    # Interpret the sentiment based on the polarity score
    sentiment = interpret_sentiment_polarity(sentiment_polarity)

    # Print the sentiment and its polarity score
    print(f"Sentiment: {sentiment} (Polarity Score: {sentiment_polarity})")

    # TODO: Distinguish between sentiment of corpus and output text
    # Display the sentiment score graphically
    display_polarity_graph(sentiment_polarity)

    return sentiment_polarity


def analyze_sentiment_by_sentence(corpus_as_string):
    """
    **This function is optimized for analyzing longer strings.**

    Analyze the sentiment of each sentence in a text and return the average sentiment.

    The function uses the TextBlob library to split the text into sentences, analyze the sentiment polarity
    of each sentence, and then average the sentiment polarity scores for the whole text.

    Parameters:
        corpus_as_string (str): The text to analyze.

    Returns:
        float: The average sentiment polarity of the sentences in the text.
    """

    # Create a TextBlob object for the given text
    analysis = TextBlob(corpus_as_string)

    # Split the text into sentences
    sentences = analysis.sentences

    # Initialize variables to keep track of total sentiment polarity and subjectivity
    total_sentiment_polarity = 0
    total_subjectivity = 0

    # Loop through each sentence in the text
    for i, sentence in enumerate(sentences):

        # Get the sentiment polarity of the sentence
        sentiment_polarity = sentence.sentiment.polarity

        # Add the sentiment polarity of the sentence to the total sentiment polarity
        total_sentiment_polarity += sentiment_polarity

        # Get the subjectivity of the sentence
        subjectivity = sentence.sentiment.subjectivity

        # Add the subjectivity of the sentence to the total subjectivity
        total_subjectivity += subjectivity

    # Calculate the average sentiment polarity
    average_sentiment_polarity = total_sentiment_polarity / len(sentences)

    # Calculate the average subjectivity
    average_subjectivity = total_subjectivity / len(sentences)

    return average_sentiment_polarity,  average_subjectivity


def interpret_sentiment_polarity(sentiment_polarity):
    """
    Interpret the sentiment based on the polarity score.

    Polarity typically ranges from -1 (very negative) to +1 (very positive),
    with 0 being neutral. This function adds granularity by distinguishing
    somewhat positive and somewhat negative values.

    Parameters:
        sentiment_polarity (float): A sentiment polarity score from -1 to 1.

    Returns:
        str: The interpreted sentiment which can be 'Positive', 'Somewhat Positive',
    'Neutral', 'Somewhat Negative', or 'Negative'.
    """

    if sentiment_polarity > 0.5:
        sentiment = "positive"
    elif 0 < sentiment_polarity <= 0.5:
        sentiment = "somewhat positive"
    elif 0 > sentiment_polarity >= -0.5:
        sentiment = "somewhat negative"
    elif sentiment_polarity < -0.5:
        sentiment = "negative"
    else:
        sentiment = "emotionally neutral"
    return sentiment


def interpret_sentiment_subjectivity(sentiment_subjectivity):
    """
    Interpret the sentiment based on the subjectivity score.

    Subjectivity typically ranges from 0 (very objective) to 1 (very subjective).
    This function adds granularity by distinguishing somewhat subjective and somewhat
    objective values.

    Parameters:
        sentiment_subjectivity (float): A sentiment subjectivity score from 0 to 1.

    Returns:
        str: The interpreted sentiment which can be 'Subjective', 'Somewhat Subjective',
    'Neutral', 'Somewhat Objective', or 'Objective'.
    """

    if sentiment_subjectivity > 0.7:
        sentiment = "subjective"
    elif 0.5 < sentiment_subjectivity <= 0.7:
        sentiment = "somewhat subjective"
    elif 0.3 < sentiment_subjectivity <= 0.5:
        sentiment = "has balanced subjectivity"
    elif 0 < sentiment_subjectivity <= 0.3:
        sentiment = "somewhat objective"
    else:
        sentiment = "objective"
    return sentiment
