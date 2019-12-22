from operator import add
from DRP.models import PerformedReaction, LabGroup, ModelContainer, BoolRxnDescriptorValue, Reaction
import datetime

# Labs included in this list will be totally ignored in the end visualization
DISCLUDED_LABS = ['default_amines']


def make_dates_csv(
        csv_name,
        inserted_or_performed,
        cumulative=False,
        count_no_data=False):
    """Gather data from a csv.

    No currently in use.
    End result is a csv in static/csv_name with headers:
    date, Norquist Group,...,allthelabgroups
    """
    no_datePerformed = {}

    # get all the potential labgroups ignoring group in DISCLUDED_LABS
    all_labGroups = []
    for lab_group in LabGroup.objects.all():
        lab_group = str(lab_group)
        if lab_group in DISCLUDED_LABS:
            continue
        all_labGroups.append(lab_group)

    # give them an index; this is how we will differentiate them in a list
    # later
    lab_group_index_dict = {}
    index = 0
    for lab_group in all_labGroups:
        lab_group_index_dict[lab_group] = index
        index += 1

    with open('static/' + csv_name, 'w') as f:
        # generate a dictionary of dates (year month day format) that has the
        # counts of each of the labgroups as values
        date_dictionary = {}
        for reaction in PerformedReaction.objects.all():
            if inserted_or_performed == "inserted":
                date = str(reaction.insertedDateTime)[:10]
            elif inserted_or_performed == "performed":
                date = str(reaction.performedDateTime)[:10]
            else:
                raise ValueError(
                    "Argument 'inserted_or_performed' must be 'inserted' or 'performed'")

            # many dates are 'None', I keep those separate
            if date == 'None' and count_no_data:
                date = str(reaction.insertedDateTime)[:10]
                if date not in no_datePerformed:
                    no_datePerformed[date] = len(all_labGroups) * [0]
                lab_group = str(reaction.labGroup)
                if lab_group in DISCLUDED_LABS:
                    continue
                lab_group_index = lab_group_index_dict[lab_group]
                no_datePerformed[date][lab_group_index] += 1
                continue
            elif date == 'None':
                continue

            if date not in date_dictionary:
                date_dictionary[date] = len(all_labGroups) * [0]

            lab_group = str(reaction.labGroup)
            if lab_group in DISCLUDED_LABS:
                continue
            lab_group_index = lab_group_index_dict[lab_group]
            date_dictionary[date][lab_group_index] += 1

        # write the headers
        f.write("date," + ",".join(all_labGroups) + "\n")
        if cumulative:
            previous = len(all_labGroups) * [0]
            ordered_dates = []
            # write the dates and corresponding entry counts
            for date in date_dictionary:
                ordered_dates.append((date, date_dictionary[date]))
            ordered_dates.sort()
            for date in ordered_dates:
                cumulative_counts = list(map(add, date[1], previous))
                previous = cumulative_counts
                lab_group_counts = map(str, cumulative_counts)
                f.write(date[0] + "," + ",".join(lab_group_counts) + "\n")
        else:
            # write the dates and corresponding entry counts
            for date in date_dictionary:
                lab_group_counts = map(str, date_dictionary[date])
                f.write(date + "," + ",".join(lab_group_counts) + "\n")
    if count_no_data:
        with open("static/noPerformedDate.csv", 'w') as f:
            # write the headers
            f.write("date," + ",".join(all_labGroups) + "\n")
            # write the dates and corresponding entry counts
            for date in no_datePerformed:
                lab_group_counts = map(str, no_datePerformed[date])
                f.write(date + "," + ",".join(lab_group_counts) + "\n")


def make_dates_csv_no_lab(
        csv_name,
        inserted_or_performed,
        cumulative=False,
        add_inbetween_times=False,
        dateRange=None):
    """Generate a dates csv without accounting for the different labs.

    Used the create the line graph next to the number of experiments.
    Not tested throughly, but tested.
    """
    with open('static/' + csv_name, 'w') as f:
        date_dictionary = {}
        if add_inbetween_times:
            if dateRange:
                d1 = dateRange[0]
                d2 = dateRange[1]
            else:
                d1 = datetime.date(2015, 7, 8)
                d2 = datetime.date(2018, 1, 21)
            delta = d2 - d1

            for i in range(delta.days + 1):
                date_dictionary[str(d1 + datetime.timedelta(i))[:10]] = 0
        for reaction in PerformedReaction.objects.all():
            if inserted_or_performed == "inserted":
                date = reaction.insertedDateTime
            elif inserted_or_performed == "performed":
                date = reaction.performedDateTime
            else:
                raise ValueError(
                    "Argument 'inserted_or_performed' must be 'inserted' or 'performed'")

            if date is None or (
                dateRange and (
                    date < dateRange[0] or date > dateRange[1])):
                continue

            date = str(date)[:10]
            if date not in date_dictionary:
                date_dictionary[date] = 0
            date_dictionary[date] += 1

        # write the headers
        f.write("date,count\n")
        if cumulative:
            previous = 0
            ordered_dates = []
            # write the dates and corresponding entry counts
            for date in date_dictionary:
                ordered_dates.append((date, date_dictionary[date]))
            ordered_dates.sort()
            for date in ordered_dates:
                cumulative_count = date[1] + previous
                previous = cumulative_count
                f.write(date[0] + "," + str(cumulative_count) + "\n")

        else:
            for date in date_dictionary:
                f.write(date + "," + str(date_dictionary[date]) + "\n")


def make_dates_csv_weekly(
        csv_name,
        inserted_or_performed,
        cumulative=False,
        dateRange=None,
        count_no_data=False):
    """Group data entries by week and create a csv.

    Now the predominately used function.
    End result is a csv in static/csv_name with headers:
    date, Norquist Group,...,allthelabgroups
    """
    # weekly is in the function name because that is the timeframe that makes the most sense
    # but you can actually specify the time window to group by here
    timewindow = 7

    # this dictionary will be used to create the csv that keeps track of the
    # "None" performedDates
    no_datePerformed = {}

    # get all the potential labgroups ignoring group in DISCLUDED_LABS
    all_labGroups = []
    for lab_group in LabGroup.objects.all():
        lab_group = str(lab_group)
        if lab_group in DISCLUDED_LABS:
            continue
        all_labGroups.append(lab_group)

    # give them an index; this is how we will differentiate them in a list
    # later
    lab_group_index_dict = {}
    index = 0
    for lab_group in all_labGroups:
        lab_group_index_dict[lab_group] = index
        index += 1

    with open('static/' + csv_name, 'w') as f:
        date_dictionary = {}
        # make a dictionary of week separated dates
        d1 = datetime.date(2015, 7, 8)
        d2 = datetime.date.today()
        delta = d2 - d1

        # I add timewindow on to guarantee that the end of the range is
        # included, but I'm not sure if that works. It close to works for sure.
        for i in range(0, delta.days + timewindow, timewindow):
            date_dictionary[str(d1 + datetime.timedelta(i))
                            [:10]] = len(all_labGroups) * [0]

        # now iterate through the reaction, rounding UP to the nearest week
        # defined above
        for reaction in PerformedReaction.objects.all():
            if inserted_or_performed == "inserted":
                date = reaction.insertedDateTime
            elif inserted_or_performed == "performed":
                date = reaction.performedDateTime
            else:
                raise ValueError(
                    "Argument 'inserted_or_performed' must be 'inserted' or 'performed'")
            # for reactions with no performed date, just use the inserted date
            if date is None:
                date = reaction.insertedDateTime
                if count_no_data:
                    date_as_string = str(reaction.insertedDateTime)[:10]
                    if date_as_string not in no_datePerformed:
                        no_datePerformed[date_as_string] = len(
                            all_labGroups) * [0]
                    lab_group = str(reaction.labGroup)
                    if lab_group in DISCLUDED_LABS:
                        continue
                    lab_group_index = lab_group_index_dict[lab_group]
                    no_datePerformed[date_as_string][lab_group_index] += 1

            # to round up, we just add one to the date until it works
            # I actually do think this is a good way of doing that
            date_as_string = str(date)[:10]
            count = 0
            while(date_as_string not in date_dictionary):
                date += datetime.timedelta(days=1)
                date_as_string = str(date)[:10]
                if count > timewindow:
                    print("Uh oh, something went wrong")
                    print(
                        "Just trying to continue... But please be alarmed. Investigate this date being on the border of the timeframe")
                    break
                count += 1

            # get the lab group and check to make sure we aren't discluding it
            lab_group = str(reaction.labGroup)
            if lab_group in DISCLUDED_LABS:
                continue

            lab_group_index = lab_group_index_dict[lab_group]
            date_dictionary[date_as_string][lab_group_index] += 1

        # write the headers
        f.write("date," + ",".join(all_labGroups) + "\n")
        if cumulative:
            previous = len(all_labGroups) * [0]
            ordered_dates = []
            # write the dates and corresponding entry counts
            for date in date_dictionary:
                ordered_dates.append((date, date_dictionary[date]))
            ordered_dates.sort()
            for date in ordered_dates:
                cumulative_counts = list(map(add, date[1], previous))
                previous = cumulative_counts
                lab_group_counts = map(str, cumulative_counts)

                # if we have a dateRange and it falls outside the date range we
                # don't want it
                if (dateRange and (datetime.datetime.strptime(
                        date[0], "%Y-%m-%d") < dateRange[0] or datetime.datetime.strptime(date[0], "%Y-%m-%d") > dateRange[1])):
                    continue

                f.write(date[0] + "," + ",".join(lab_group_counts) + "\n")
        else:
            # write the dates and corresponding entry counts
            for date in date_dictionary:
                lab_group_counts = map(str, date_dictionary[date])

                # if we have a dateRange and it falls outside the date range we
                # don't want it
                if (dateRange and (datetime.datetime.strptime(date,
                                                              "%Y-%m-%d") < dateRange[0] or datetime.datetime.strptime(date,
                                                                                                                       "%Y-%m-%d") > dateRange[1])):
                    continue

                f.write(date + "," + ",".join(lab_group_counts) + "\n")
    if count_no_data:
        with open("static/noPerformedDate.csv", 'w') as f:
            # write the headers
            f.write("date," + ",".join(all_labGroups) + "\n")
            # write the dates and corresponding entry counts
            for date in no_datePerformed:
                lab_group_counts = map(str, no_datePerformed[date])
                f.write(date + "," + ",".join(lab_group_counts) + "\n")


def make_valid_reaction_csv(csv_name):
    """Create the valid reaction csv.

    Headers are "date,True,False,None"
    I made this in haste, but it should still be pretty nice.
    Add to it as needed.
    """
    timewindow = 7

    date_dictionary = {}
    # make a dictionary of week separated dates
    d1 = datetime.date(2015, 7, 8)
    d2 = datetime.date.today()
    delta = d2 - d1

    # I add timewindow on to guarantee that the end of the range is included,
    # but I'm not sure if that works. It close to works for sure.
    for i in range(0, delta.days + timewindow, timewindow):
        date_dictionary[str(d1 + datetime.timedelta(i))[:10]] = 2 * [0]

    # True will be the index 0, False 1, and None 2
    index_key_dictionary = {True: 0, False: 1}
    with open('static/' + csv_name, 'w') as f:

        # now iterate through the reaction, rounding UP to the nearest week
        # defined above
        for reaction in PerformedReaction.objects.all():
            date = reaction.insertedDateTime

            # to round up, we just add one to the date until it works
            # I actually do think this is a good way of doing that
            date_as_string = str(date)[:10]
            count = 0
            while(date_as_string not in date_dictionary):
                date += datetime.timedelta(days=1)
                date_as_string = str(date)[:10]
                if count > timewindow:
                    print("Uh oh, something went wrong")
                    print(
                        "Just trying to continue... But please be alarmed. Investigate this date being on the border of the timeframe")
                    break
                count += 1
            index = index_key_dictionary[reaction.valid]
            date_dictionary[date_as_string][index] += 1

        # write the headers
        f.write("date,Valid,Invalid\n")
        previous = 2 * [0]
        ordered_dates = []
        # write the dates and corresponding entry counts
        for date in date_dictionary:
            ordered_dates.append((date, date_dictionary[date]))
        ordered_dates.sort()
        for date in ordered_dates:
            cumulative_counts = list(map(add, date[1], previous))
            previous = cumulative_counts
            valid_invalid_counts = map(str, cumulative_counts)
            f.write(date[0] + "," + ",".join(valid_invalid_counts) + "\n")
