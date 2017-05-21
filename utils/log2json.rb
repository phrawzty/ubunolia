#!/usr/bin/env ruby

require 'json'
require 'optparse'
require 'httpclient'

# Set runtime options.
options = {}
OptionParser.new do |opts|
    opts.banner = "Convert a day's worth of Ubuntu IRC logs to JSON.\nUsage: log2json.rb --date YYYY-MM-DD [options]\n"

    opts.on('-d', '--date YYYY-MM-DD', 'REQUIRED: Datestamp') { |v|
        options[:datestamp] = v
    }
    options[:channels] = "ubuntu,kubuntu,xubuntu"
    opts.on('-c', '--channels CHANNEL[,CHANNEL]', "Channels to nab. Default: #{options[:channels]}") { |v|
        options[:channels] = v
    }

    opts.on('-h', '--help', 'This help.') do
        puts opts
        exit 1
    end
end.parse!

# Require some runtime args.
if not (options[:datestamp]) then
    puts 'ERROR: Must specify datestamp. See --help'
    exit 1
end

# Parse the channel list
channel_list = options[:channels].split(',')

# Make a URL out of the datestamp.
options[:datestamp] =~ /(\d+)-(\d+)-(\d+)/
base_url = "https://irclogs.ubuntu.com/#{$1}/#{$2}/#{$3}/"

# Use HTTPClient because the algoliasearch gem already brought it to the party.
clnt = HTTPClient.new

# Slurp down some logs.
channel_list.each do |channel|
    puts 'Processing: ' + base_url + channel + '.txt'

    # Use the filesystem as a cache because why not?
    File.open(channel + '.txt', 'w') { |file|
        file.write(clnt.get(base_url + '%23' + channel + '.txt').body)
    }
end

# Set up our utility variables.
counter = 0
log_array = []

# Parse the newly acquired channel logs.
channel_list.each do |channel|
    File.open(channel + '.txt').each do |line|

        # Parse log line and look for HH:MM timestamp, username, and message (in
        # that order). I <3 regex and I'm not ashamed to admit it.
        if line =~ /\[(\d\d:\d\d)\]\s<(\w+)\>\s(.*)$/ then
            # Fake SS:NN for a more granular timestamp.
            faketime = "%04d" % counter.to_s
            faketime = faketime.insert(2, '.')

            # Create a log item for eventual JSONisation.
            log_array.push({
                :datestamp => "#{options[:datestamp]}T#{$1}:#{faketime}",
                :channel => channel,
                :username => $2,
                :message => $3
            })
            counter +=1
        end
    end
end

# Dump that glorious hash out to a json file.
File.open(options[:datestamp] + '.json', 'w') { |file| file.write(log_array.to_json) }

# Hooray! We made it to the end without any serious injuries!
exit 0
