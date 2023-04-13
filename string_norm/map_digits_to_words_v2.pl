### Radboud University, CLST, Nijmegen, NL
### developed for internal R&D purposes 2010-2019
### Available under license Affero GLP v3.0 (AGPL-3.0)
# maps all numbers into verbal expressions


while (<STDIN>)
  {
  chomp;
  @result = ();
  @tok = split(/\s+/);

  for ($i = 0; $i <= $#tok; $i++)
    {
    if ($tok[$i] =~ m/^[\.\,\-0-9]+$/)
      {
      $tok[$i] = &num2str($tok[$i]);
      push(@result, $tok[$i]);
      }
    else
      {push(@result, $tok[$i]);}
    }
  printf("%s\n", join(" ", @result));
  }


sub num2str
{
my @arg = @_;
my $word = $arg[0];
my $a;
my $b;
my $c;
my $tmp;

#printf("now handling %s\n", $word);
  $word =~ s/^0$/nul/;
  $word =~ s/^1$/een/;
  $word =~ s/^2$/twee/;
  $word =~ s/^3$/drie/;
  $word =~ s/^4$/vier/;
  $word =~ s/^5$/vijf/;
  $word =~ s/^6$/zes/;
  $word =~ s/^7$/zeven/;
  $word =~ s/^8$/acht/;
  $word =~ s/^9$/negen/;
  $word =~ s/^10$/tien/;
  $word =~ s/^11$/elf/;
  $word =~ s/^12$/twaalf/;
  $word =~ s/^13$/dertien/;
  $word =~ s/^14$/veertien/;
  $word =~ s/^15$/vijftien/;
  $word =~ s/^16$/zestien/;
  $word =~ s/^17$/zeventien/;
  $word =~ s/^18$/achttien/;
  $word =~ s/^19$/negentien/;
  $word =~ s/^20$/twintig/;
  $word =~ s/^30$/dertig/;
  $word =~ s/^40$/veertig/;
  $word =~ s/^50$/vijftig/;
  $word =~ s/^60$/zestig/;
  $word =~ s/^70$/zeventig/;
  $word =~ s/^80$/tachtig/;
  $word =~ s/^90$/negentig/;
  $word =~ s/^100$/honderd/;
  $word =~ s/^1000$/duizend/;
  $word =~ s/^10000$/tienduizend/;
  $word =~ s/^100000$/honderdduizend/;
  $word =~ s/^1000000$/miljoen/;
  $word =~ s/^10000000$/tien miljoen/;
  $word =~ s/^100000000$/honderd miljoen/;


    if ($word =~ m/^([0-9])([0-9])$/)
      {
      $a = $1; $b = $2;
      if ($a > 0)
        { $word = &num2str($b) . " en " . &num2str($a . "0"); }
      else
        { $word = &num2str($a) . " " . &num2str($b); }
      }

    if ($word =~ m/^([0-9])([0-9][0-9])$/)
      {
      $a = $1; $b = $2;
      if ($a > 1)
        { $word = &num2str($a) . " honderd " . &num2str(&fapz($b)); }
      else
        {
	if ($a == 1)
          { $word = "honderd " . &num2str(&fapz($b)); }
        else
	  { $word = &num2str($a) . " " . &num2str(&fapz($b)); }
	}
      }

    if ($word =~ m/^(0+)(.+)$/)
      {
      $a = $1;
      $b = $2;
      $tmp = "";
      for ($i = 1; $i <= length($a); $i++)
        { $tmp = $tmp . "nul ";}
      for ($i = 0; $i < length($b); $i++)
        { $tmp = $tmp . " " .  &num2str(substr($b, $i, 1)); }

      $word = $tmp;
      }



    if ($word =~ m/^([1-9])([0-9])([0-9][0-9])$/)
      {
      $a = $1; $b = $2; $c = $3;
      if (($a == 1) & ($b == 0))
        { $word = "duizend " . &num2str(&fapz($c)); }
      else
        {
	if ($b == 0)
          { $word = &num2str($a) . " duizend " . &num2str(&fapz($c)); }
        else
	  { $word = &num2str($a . $b) . " honderd " . &num2str(&fapz($c)); }
	}
      }

    if ($word =~ m/^([1-9][0-9])([0-9][0-9][0-9])$/)
      {
      $a = $1; $b = $2;
      $word = &num2str($a) . " duizend " . &num2str(&fapz($b));
      }

    if ($word =~ m/^([1-9][0-9][0-9])([0-9][0-9][0-9])$/)
      {
      $a = $1; $b = $2;
      $word = &num2str($a) . " duizend " . &num2str(&fapz($b));
      }

    if ($word =~ m/^([1-9])([0-9][0-9][0-9][0-9][0-9][0-9])$/)
      {
      $a = $1; $b = $2;
      $word = &num2str($a) . " miljoen " . &num2str(&fapz($b));
      }

    if ($word =~ m/^([1-9][0-9])([0-9][0-9][0-9][0-9][0-9][0-9])$/)
      {
      $a = $1; $b = $2;
      $word = &num2str($a) . " miljoen " . &num2str(&fapz($b));
      }

    if ($word =~ m/^([1-9][0-9][0-9])([0-9][0-9][0-9][0-9][0-9][0-9])$/)
      {
      $a = $1; $b = $2;
      $word = &num2str($a) . " miljoen " . &num2str(&fapz($b));
      }

  if ($word =~ m/^(.+)\,(.+)$/)
      {
      $a = $1; $b = $2;
      $word = &num2str($a) . " komma " . &num2str(&fapz($b));
      }

  if ($word =~ m/^(.+)\.(.+)$/)
      {
      $a = $1; $b = $2;
      $word = &num2str($a) . " punt " . &num2str(&fapz($b));
      }

  if ($word =~ m/^\-(.+)$/)
      {
      $a = $1;
      $word = "min " . &num2str($a);
      }



#printf("result %s\n", $word);
return $word;
}


sub fapz # forget about prepending zeroes
{
my $arg = @_[0];
$arg =~ s/^[0]+//g;
return $arg;
}
