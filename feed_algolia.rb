#!/usr/bin/env ruby

require 'optparse'
require 'algoliasearch'

# Set runtime options.
options = {}
OptionParser.new do |opts|
    opts.banner = "Feed delicious JSON noms to Algolia.\nUsage: feed_algolia.rb --id ID --key KEY --index INDEX --source SOURCE\n"

    opts.on('--id ID', 'Application ID') { |v|
        options[:id] = v
    }
    opts.on('--key KEY', 'API Key (r/w)') { |v|
        options[:key] = v
    }
    opts.on('--index INDEX', 'Name of index') { |v|
        options[:index] = v
    }
    opts.on('--source SOURCE', 'File with the JSON in it') { |v|
        options[:source] = v
    }

    opts.on('-h', '--help', 'This help') do
        puts opts
        exit 1
    end
end.parse!

# Require some runtime args.
if not (options[:id] or options[:key] or options[:index] or options[:source]) then
    puts 'ERROR: Must specify id, key, index, and source. See --help'
    exit 1
end

# Initialise the Algolia handler.
Algolia.init :application_id => options[:id],
             :api_key        => options[:key]

# Feed me, Seymour!
puts 'Processing: ' + options[:source] + ' to ' + options[:index]
index = Algolia::Index.new(options[:index])
batch = JSON.parse(File.read(options[:source]))
index.add_objects(batch)

exit 0
